# MOTION GATE — f

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\ai-slower-useful-faster\build-private\f ===
               runtime: 1:12
         visual_events: 235 (193.3/min)
                 docks: 4
           dock_source: timeline
          ledger_pages: 9
  still_over_12s_share: 0%
            per_minute: 0:00:193/12

  [WARN ] M06 60 caption pages = 49/min, 4.0 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [WARN ] M11 first chart ledger:s02 enters at 8.7s, its build lands at 11.7s, with spotlight at 12.9s; WARN no sound cue within 1.5s of the enter at 8.7s; window 0-10s (E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10)
          E24 / doc 29 s9.29 (long form) + E44 (short): the first chart enters 0:08-0:20, or 0:00-0:10 on a short, annotated on its divergence, with a sound cue
  [WARN ] M22 8 push(es) tied to nothing: s03 punch at 0:14; s04 punch at 0:20; s05 punch at 0:30; s06 punch at 0:36; s07 punch at 0:42; s08 punch at 0:50; s09 punch at 0:57; s10 punch at 1:04 - a push lands ON a thing that just landed (a badge, a datum, a bracket, a card) or it is cut
          E51 (operator 2026-09-07): a push-in is only used tied to something - pushing into a newly landed badge or data series; a zoom on a thing that just sits there is filler
  [WARN ] M25 1 safe-zone intrusion(s) over 59 instants probed: a card is 28 % inside the right safe-zone band at 0:11
          E45 s1 (the compiler's `place`: a card parks in the page's quiet space, never over the plot, the title, the source line or the caption's anchor) / E52 (the page CITES: the citation rides the park) / E60 - the three defects of 2026-09-10, refused from the page's own DOM (probe.py --gate)
  [WARN ] M34 1 reading(s) over 59 instants probed: sname:p = 95% per st across its own line s0 at 0:15 (s03), 148 px from the line's end (a direct label sits within 118)
          K9, the operator's reasoning items C05-R023 ("every text element must be in the collision ledger, including the ones that were already there"; "labels are all crashing with the lines") and C09-R003 ("the callout owns its position"; measure the rendered boxes, never estimate), and the two defects no row caught on normal-for-which-bridge review-v1 (docs/agent-memory/operator/casebook/ring-on-the-tip-label: the dashed 123% ring painted over "x3.9 Federal debt" at 0:57; .../name-on-the-neighbour-line: "10-year" written across the 30-year line at 0:19, the 4.83% arc clipping it). M28 pairs labels with labels; this row puts every text box against every mark's stroke and every series polyline, from the page's own DOM (probe.py --gate). The operator, 2026-09-13: "bracket should probably be able to bypass that rule" - a bracket's or a figure's own text on the series it measures is allowed (on a DIFFERENT series' line it still FAILs); and "a ring or callout drawn over a label doesn't automatically fail, if the point is to draw a ring or highlight around that label - but we have spotlight tools that can provide more clarity while demanding less accuracy" - a mark over its OWN target's text (the datum it rings: a bar's value, its pill, a figure or bracket at that datum) WARNs and names the spotlight (E56: a ring circles a number or a point on a chart); over any other text it FAILs
  [PASS ] M01 longest still stretch 2.2s at 0:52
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 10s from 0:20
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 10 distinct plates; target runtime/12s = 6
          doc 29 s9.13 plate density
  [PASS ] M05 no plate over the 20s hold
          doc 29 s9.13 as amended by E69 (2026-09-12): the hold is legal while the FRAME LIVES - the ceiling's two-dock condition was written when a world was a still and only a card could move on it
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
  [PASS ] M16 longest gap between visual events 2.2s at 0:52; 0 gap(s) over 2.5s
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [PASS ] M21 every ledger page leaves or un-draws within 8s of its last data mark: s02 2.2s (0:11 -> 0:13); s03 5.1s (0:15 -> 0:20); s04 6.6s (0:23 -> 0:30); s05 0.5s (0:35 -> 0:36); s06 5.0s (0:37 -> 0:42); s07 6.3s (0:44 -> 0:50); s08 4.8s (0:52 -> 0:56); s09 6.3s (0:58 -> 1:04)
          E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing
  [PASS ] M23 1 transition(s), each on a built chart and clear of its page's edge: s05 recast 0:34+1.1s
          P48 (operator 2026-09-07): chart-to-chart transitions are a first-rate feature - a chart changes STATE and never cuts; E45/E50: never over a build, never inside the last 0.5 s of a page's life
  [PASS ] M26 87 printed value(s) over 59 instants probed agree with the height drawn on the scale the page prints (band 4% of the top tick + the burst's 5% overshoot); worst 2.3% of the top tick - 8 at 0:44
          E28 (a chart reads right at a glance: a bar's height IS its value) / E53 (the scale and the value are printed at every instant) / R26-40 - the printed number and the DRAWN height, read against the scale the page itself prints, from the page's own DOM (probe.py --gate). R26-39 was exactly this mismatch: 303 px of bar at "0.00 %"
  [PASS ] M27 no card reads over a ledger page's ink over 59 instants probed (5 not-parked card reading(s) measured)
          E63 (operator 2026-09-11, on the Tokyo cut at 0:09.5-0:10.5: "docking over the plate while it's drawing is not a good standard practice ... as a rule we should probably use better handling now that we can manipulate scale/depth/placement easier"; widened the same evening, on the read that came back over the finished chart: "im confused, because you just left the dock over the chart now too. something went backwards"): a card that has not parked yet may not sit on a ledger page's INK, drawing or finished - the READ moves (the compiler's `read_moved` / `read_deferred`), never the word. The page's own INK is what the row scores (the data, the labels, the citation - M25's boxes): since E65 the placer may put a card in the plot's own empty ROOM on purpose, so the plot box is the WARN tier and the ink is the FAIL. A PARKED card is E45's contract and M25's row. Read from the page's own DOM (probe.py --gate)
  [PASS ] M28 no two of a page's own labels touch, and the value row keeps half a figure of air, over 59 instants probed (3,217 label pair(s) checked)
          R26-53 (the operator, 2026-09-11: "why are we now crashing text?") - the Tokyo Meta page's four values "$665 $633 $604 $577" touched each other and the callout's pill on bar 4 covered bar 3's label, on the approved build and on every side build before f67c5ed, and no row saw it: M25 reads cards over ink, M26 the value's height, and the probe's `overlaps` carried card-vs-ink and pill-vs-rail only. E28 (a chart reads right at a glance): no two of a page's OWN labels may sit on each other, and the row that fits them (lpFitValues / lpPillBand) leaves half a figure of air between them. From the page's own DOM (probe.py --gate)
  [PASS ] M43 8 of 8 camera landing(s) measured against 0 text box(es): every one wholly in frame or wholly out of it
          punch-crops-text (the operator, 2026-09-03, ledger 16d1b9558a10; docs/operator-ledger/TRIAGE-DIGEST.md): a text box the camera's landed frame cuts PARTWAY is a cropped word. Fully inside reads, fully outside is a choice the author made; half of a sentence hanging off the frame edge is neither. The frame is the frustum M24 computes from the row's own camera (camera_state_at + camera_frustum); the boxes are probe.py --gate's (layout-probe.json), the file M25/M26/M27/M28/M34 already read
  [PASS ] M44 every world plate holds at least 6s (1 world plate(s), floor 6s)
          sub-6s-plate (the operator, 2026-08-29, ledger 69ff558bdf67; docs/operator-ledger/TRIAGE-DIGEST.md: "the baloon dock doesn't even make sense ... why do we have a plate less than 6 seconds long?"): a world plate under 6 s is a flash the eye cannot take in, and one that also carries a DOCK asks the eye to read evidence inside that flash. BUILD-PIPELINE says only "under ~8s one piece or none" and nothing checked plate length. Read from the timeline's own scenes - no browser, no render
  [INFO ] M07 short: 1 full minute(s) in 73s - opening 193.0 events/min, 12.0 evidence entries/min; whole runtime 191.7/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M18 frozen frames not measured - run measure_frozen_frames.py <build> (writes frame-hashes.json)
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py); R26-13: read PER LAYER too - the page, the docks and the captions each on their own (frame-hashes.<layer>.json, the shell's ?layers= switch), because a caption boiling over a frozen page passes the whole-frame hash (Tokyo v2: 1036 distinct frames of 1066, M18 PASS, the pages still). The whole-frame verdict is still reported.
  [INFO ] M19 build_to caps declared; none holds between caps
          P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness
  [INFO ] M20 1 arrival(s): dock-amodei-opening throw ~2479 px/s -> on 1s
          P47 T1 + E99 s30 (the cadence rule, cinema parity): a throw steps on 1s above 154 px/s, on 2s below - reported, not scored, until HG2 tunes it
  [INFO ] M31 not measured - run measure_stage_gaps.py <build> to read the empty stage
          R26-66 / P53 T2, measured with measure_stage_gaps.py: a transition that TAKES the world (a suck, a melt) left the stage with no world on it for 3.1 s while the narration was already on the next sentence - 8.9% of a 69 s short. The DIP is the one transition licensed to empty the stage (a dip is a world change); everything else hands off, and the page that follows an inked arrival (enter=axes / built) measures 0.
  [INFO ] M32 not measured - run measure_seam_frames.py <build> to read the seams frame by frame
          P54 T9 (the operator, 2026-09-13: 'it's really the flash before or a second black frame that we're looking for'): measure_seam_frames.py seeks every boundary frame by frame; near-black = mean luma < 8 [MEASURED on the approved Japan short's six dips: darkest 0-6, cuts never under 52]. A declared dip's own dark core is the design; black anywhere else at a seam is the fault the operator found by hand twice (2026-09-05, 2026-09-12)
  [INFO ] M33 not measured - run measure_spoken_visuals.py <build>
          P54 T9 (the operator, 2026-09-13: 'gating for narration without the chart on screen is probably valid'; 2026-08-29: 'you open on the "spike" but you don't have the spike ons creen, you talk about charts without the charts on screen'): measure_spoken_visuals.py - a pointing phrase needs a page, a dock or a card on stage. WARN until the approved shorts show a real example (their one hit is a figure of speech)
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 0 FAIL / 5 WARN / 19 PASS / 1 JUDGE / 7 INFO
```

TIMELINE: ai-slower-useful-faster-f.timeline.json sha256:d455d7220f6315e9f9804417194df1aba54c79484f118f9419324d9238e04147
VERDICT: PASS (0 FAIL)
