# MOTION GATE — build-oneshot-3

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\memory-trades-the-calendar\build-oneshot-3 ===
               runtime: 1:17
         visual_events: 222 (171.6/min)
                 docks: 5
           dock_source: timeline
          ledger_pages: 6
  still_over_12s_share: 0%
            per_minute: 0:00:178/9

  [FAIL ] M16 longest gap between visual events 4.2s at 0:58; 1 gap(s) over 2.5s: 0:58+4.2s - add motion there (a species, a caption pop, plate life); never cut motion to pass
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [FAIL ] M25 1 layout fault(s) over 46 instants probed: chart.lab type at 10.6 CSS px on a phone at 0:39 (floor 11, 29 stage px) | INFO, listed not scored (CSS px on a phone): source (the citation) 9.4
          E45 s1 (the compiler's `place`: a card parks in the page's quiet space, never over the plot, the title, the source line or the caption's anchor) / E52 (the page CITES: the citation rides the park) / E60 - the three defects of 2026-09-10, refused from the page's own DOM (probe.py --gate)
  [FAIL ] M28 17 pair(s) of a page's own labels sitting on each other over 46 instants probed: tick:Dec on val:-12.4% at 0:44 (s06), 1,152 px, 36 % of the smaller label; tick:Oct '24 on tick:Dec at 0:44 (s06), 880 px, 28 % of the smaller label; tick:Oct '24 on val:-12.4% at 0:44 (s06), 768 px, 14 % of the smaller label; val:-12.4% on tick:Jan at 0:44 (s06), 304 px, 11 % of the smaller label; val:10.9% on pill:-13.8% at 0:44 (s06), 300 px, 6 % of the smaller label; val:-10.5% and val:-11.3% at 0:44 (s06), 0 px of air - under a quarter of a figure (6 at 40 px): the eye reads one string (R26-53) ... - fit the row (lpFitValues), raise the pill to its band (lpPillBand) or move the label; a number on a number is not a number
          R26-53 (the operator, 2026-09-11: "why are we now crashing text?") - the Tokyo Meta page's four values "$665 $633 $604 $577" touched each other and the callout's pill on bar 4 covered bar 3's label, on the approved build and on every side build before f67c5ed, and no row saw it: M25 reads cards over ink, M26 the value's height, and the probe's `overlaps` carried card-vs-ink and pill-vs-rail only. E28 (a chart reads right at a glance): no two of a page's OWN labels may sit on each other, and the row that fits them (lpFitValues / lpPillBand) leaves half a figure of air between them. From the page's own DOM (probe.py --gate)
  [FAIL ] M34 5 collision(s) over 46 instants probed: tick:200 on line s1 at 1:08 (s11) - a text box on a line it does not name; tick:Feb on line s1 at 1:08 (s11) - a text box on a line it does not name; tick:Jun on line s0 at 1:08 (s11) - a text box on a line it does not name; tick:Jun on line s1 at 1:08 (s11) - a text box on a line it does not name; tick:Aug on line s1 at 1:08 (s11) - a text box on a line it does not name - a mark rings its datum and never a word; a name names the line it touches (the line builder's tip clearance and its side away from a neighbour, 41bf55c)
          K9, the operator's reasoning items C05-R023 ("every text element must be in the collision ledger, including the ones that were already there"; "labels are all crashing with the lines") and C09-R003 ("the callout owns its position"; measure the rendered boxes, never estimate), and the two defects no row caught on normal-for-which-bridge review-v1 (docs/agent-memory/operator/casebook/ring-on-the-tip-label: the dashed 123% ring painted over "x3.9 Federal debt" at 0:57; .../name-on-the-neighbour-line: "10-year" written across the 30-year line at 0:19, the 4.83% arc clipping it). M28 pairs labels with labels; this row puts every text box against every mark's stroke and every series polyline, from the page's own DOM (probe.py --gate). The operator, 2026-09-13: "bracket should probably be able to bypass that rule" - a bracket's or a figure's own text on the series it measures is allowed (on a DIFFERENT series' line it still FAILs); and "a ring or callout drawn over a label doesn't automatically fail, if the point is to draw a ring or highlight around that label - but we have spotlight tools that can provide more clarity while demanding less accuracy" - a mark over its OWN target's text (the datum it rings: a bar's value, its pill, a figure or bracket at that datum) WARNs and names the spotlight (E56: a ring circles a number or a point on a chart); over any other text it FAILs
  [WARN ] M44 4 world plate(s) under 6s (5 world plate(s), floor 6s): s02 5.8s, s03 2.1s, s07 1.3s, s10 3.3s - a plate the eye cannot take in; lengthen it or fold it into its neighbour
          sub-6s-plate (the operator, 2026-08-29, ledger 69ff558bdf67; docs/operator-ledger/TRIAGE-DIGEST.md: "the baloon dock doesn't even make sense ... why do we have a plate less than 6 seconds long?"): a world plate under 6 s is a flash the eye cannot take in, and one that also carries a DOCK asks the eye to read evidence inside that flash. BUILD-PIPELINE says only "under ~8s one piece or none" and nothing checked plate length. Read from the timeline's own scenes - no browser, no render
  [PASS ] M01 longest still stretch 4.2s at 0:58
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 17s from 0:00
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 11 distinct plates; target runtime/12s = 6
          doc 29 s9.13 plate density
  [PASS ] M05 no plate over the 20s hold
          doc 29 s9.13 as amended by E69 (2026-09-12): the hold is legal while the FRAME LIVES - the ceiling's two-dock condition was written when a world was a still and only a card could move on it
  [PASS ] M06 50 caption pages = 39/min, 4.5 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M08 timeline declares cap_mode; every stretch over the ceiling carries stage captions (counted as events above)
          doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves)
  [PASS ] M09 no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns
          doc 29 s9.27 precedence / s9.28 C3: one camera move per window
  [PASS ] M10 no still stretch > 6s begins in the first 60s
          E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s
  [PASS ] M11 first chart ledger:s01 enters at 0.0s, its build lands at 3.0s, with spotlight at 3.3s; window 0-10s (E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10)
          E24 / doc 29 s9.29 (long form) + E44 (short): the first chart enters 0:08-0:20, or 0:00-0:10 on a short, annotated on its divergence, with a sound cue
  [PASS ] M12 no chart dock spans a scene boundary or holds past 10s (6s in the opening minute)
          E25 / doc 29 s9.30: the chart is the proof, not the homework
  [PASS ] M14 no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal
          47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move
  [PASS ] M15 no species window overlaps a page's retract
          E40 #5 (operator, 2026-09-05): no spotlight on a spiral out - no species window overlaps a page's retract
  [PASS ] M23 1 transition(s), each on a built chart and clear of its page's edge: s04 compare 0:29+0.9s
          P48 (operator 2026-09-07): chart-to-chart transitions are a first-rate feature - a chart changes STATE and never cuts; E45/E50: never over a build, never inside the last 0.5 s of a page's life
  [PASS ] M26 50 printed value(s) over 46 instants probed agree with the height drawn on the scale the page prints (band 4% of the top tick + the burst's 5% overshoot); worst 4.7% of the top tick - Jul '26 at 0:44
          E28 (a chart reads right at a glance: a bar's height IS its value) / E53 (the scale and the value are printed at every instant) / R26-40 - the printed number and the DRAWN height, read against the scale the page itself prints, from the page's own DOM (probe.py --gate). R26-39 was exactly this mismatch: 303 px of bar at "0.00 %"
  [PASS ] M27 no card reads over a ledger page's ink over 46 instants probed (18 not-parked card reading(s) measured)
          E63 (operator 2026-09-11, on the Tokyo cut at 0:09.5-0:10.5: "docking over the plate while it's drawing is not a good standard practice ... as a rule we should probably use better handling now that we can manipulate scale/depth/placement easier"; widened the same evening, on the read that came back over the finished chart: "im confused, because you just left the dock over the chart now too. something went backwards"): a card that has not parked yet may not sit on a ledger page's INK, drawing or finished - the READ moves (the compiler's `read_moved` / `read_deferred`), never the word. The page's own INK is what the row scores (the data, the labels, the citation - M25's boxes): since E65 the placer may put a card in the plot's own empty ROOM on purpose, so the plot box is the WARN tier and the ink is the FAIL. A PARKED card is E45's contract and M25's row. Read from the page's own DOM (probe.py --gate)
  [INFO ] M07 short: 1 full minute(s) in 78s - opening 178.0 events/min, 9.0 evidence entries/min; whole runtime 170.0/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M18 frozen frames not measured - run measure_frozen_frames.py <build> (writes frame-hashes.json)
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py); R26-13: read PER LAYER too - the page, the docks and the captions each on their own (frame-hashes.<layer>.json, the shell's ?layers= switch), because a caption boiling over a frozen page passes the whole-frame hash (Tokyo v2: 1036 distinct frames of 1066, M18 PASS, the pages still). The whole-frame verdict is still reported.
  [INFO ] M19 1 build_to hold(s) - the line rests at a datum until the next word: 0:51+2.2s
          P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness
  [INFO ] M21 1 page(s) deployed 8-12s after the last data mark (a dock's clip may hold it): s04 9.5s (0:21 -> 0:30)
          E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing
  [INFO ] M31 not measured - run measure_stage_gaps.py <build> to read the empty stage
          R26-66 / P53 T2, measured with measure_stage_gaps.py: a transition that TAKES the world (a suck, a melt) left the stage with no world on it for 3.1 s while the narration was already on the next sentence - 8.9% of a 69 s short. The DIP is the one transition licensed to empty the stage (a dip is a world change); everything else hands off, and the page that follows an inked arrival (enter=axes / built) measures 0.
  [INFO ] M32 not measured - run measure_seam_frames.py <build> to read the seams frame by frame
          P54 T9 (the operator, 2026-09-13: 'it's really the flash before or a second black frame that we're looking for'): measure_seam_frames.py seeks every boundary frame by frame; near-black = mean luma < 8 [MEASURED on the approved Japan short's six dips: darkest 0-6, cuts never under 52]. A declared dip's own dark core is the design; black anywhere else at a seam is the fault the operator found by hand twice (2026-09-05, 2026-09-12)
  [INFO ] M33 not measured - run measure_spoken_visuals.py <build>
          P54 T9 (the operator, 2026-09-13: 'gating for narration without the chart on screen is probably valid'; 2026-08-29: 'you open on the "spike" but you don't have the spike ons creen, you talk about charts without the charts on screen'): measure_spoken_visuals.py - a pointing phrase needs a page, a dock or a card on stage. WARN until the approved shorts show a real example (their one hit is a figure of speech)
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 4 FAIL / 1 WARN / 16 PASS / 1 JUDGE / 7 INFO
```

TIMELINE: calendar-short.timeline.json sha256:7dfa6f96584cbcfd3681c8c41c71a3cff4a83c607557d5bf6619ac23398253cc
VERDICT: FAIL (4 FAIL)
