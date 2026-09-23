# MOTION GATE — build-p58-2-5d

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\tokyo-tea-break\build-p58-2-5d ===
               runtime: 1:28
         visual_events: 309 (208.7/min)
                 docks: 6
           dock_source: timeline
          ledger_pages: 4
  still_over_12s_share: 0%
            per_minute: 0:00:220/6 1:00:183/8

  [FAIL ] M28 2 pair(s) of a page's own labels sitting on each other over 64 instants probed: tick:Jun '26 on bracket:$1,116.7B at 0:25 (s02), 1,550 px, 28 % of the smaller label; sname:-9.9% Japan on bracket:$1,116.7B at 0:25 (s02), 340 px, 4 % of the smaller label - fit the row (lpFitValues), raise the pill to its band (lpPillBand) or move the label; a number on a number is not a number
          R26-53 (the operator, 2026-09-11: "why are we now crashing text?") - the Tokyo Meta page's four values "$665 $633 $604 $577" touched each other and the callout's pill on bar 4 covered bar 3's label, on the approved build and on every side build before f67c5ed, and no row saw it: M25 reads cards over ink, M26 the value's height, and the probe's `overlaps` carried card-vs-ink and pill-vs-rail only. E28 (a chart reads right at a glance): no two of a page's OWN labels may sit on each other, and the row that fits them (lpFitValues / lpPillBand) leaves half a figure of air between them. From the page's own DOM (probe.py --gate)
  [FAIL ] M34 1 collision(s) over 64 instants probed: callout m0 over val:$665 at 1:10 (s05) - the mark's stroke is painted across the text - a mark rings its datum and never a word; a name names the line it touches (the line builder's tip clearance and its side away from a neighbour, 41bf55c)
          K9, the operator's reasoning items C05-R023 ("every text element must be in the collision ledger, including the ones that were already there"; "labels are all crashing with the lines") and C09-R003 ("the callout owns its position"; measure the rendered boxes, never estimate), and the two defects no row caught on normal-for-which-bridge review-v1 (docs/agent-memory/operator/casebook/ring-on-the-tip-label: the dashed 123% ring painted over "x3.9 Federal debt" at 0:57; .../name-on-the-neighbour-line: "10-year" written across the 30-year line at 0:19, the 4.83% arc clipping it). M28 pairs labels with labels; this row puts every text box against every mark's stroke and every series polyline, from the page's own DOM (probe.py --gate). The operator, 2026-09-13: "bracket should probably be able to bypass that rule" - a bracket's or a figure's own text on the series it measures is allowed (on a DIFFERENT series' line it still FAILs); and "a ring or callout drawn over a label doesn't automatically fail, if the point is to draw a ring or highlight around that label - but we have spotlight tools that can provide more clarity while demanding less accuracy" - a mark over its OWN target's text (the datum it rings: a bar's value, its pill, a figure or bracket at that datum) WARNs and names the spotlight (E56: a ring circles a number or a point on a chart); over any other text it FAILs
  [WARN ] M11 first chart ledger:s02 enters at 2.0s, its build lands at 7.5s, with build_to landing on datum 311 at 7.5s (the cap is the annotation: the line ends on the datum); WARN no sound cue within 1.5s of the enter at 2.0s; window 0-10s (E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10)
          E24 / doc 29 s9.29 (long form) + E44 (short): the first chart enters 0:08-0:20, or 0:00-0:10 on a short, annotated on its divergence, with a sound cue
  [WARN ] M21 1 page(s) deployed past 12s after the last data mark: s02 16.5s (0:22 -> 0:38) - un-draw it (undraw) or let it become the next thing (figure, another display, the morph)
          E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing
  [WARN ] M27 1 card(s) inside the plot's box, clear of its ink, over 64 instants probed: dock-g-two-fingers is inside the plot's box, clear of the ink, on the finished chart, at 0:36, 16,297 px, 13 % of the smaller box (marks 100% drawn) - E65's own placement; listed so the author sees where the read landed
          E63 (operator 2026-09-11, on the Tokyo cut at 0:09.5-0:10.5: "docking over the plate while it's drawing is not a good standard practice ... as a rule we should probably use better handling now that we can manipulate scale/depth/placement easier"; widened the same evening, on the read that came back over the finished chart: "im confused, because you just left the dock over the chart now too. something went backwards"): a card that has not parked yet may not sit on a ledger page's INK, drawing or finished - the READ moves (the compiler's `read_moved` / `read_deferred`), never the word. The page's own INK is what the row scores (the data, the labels, the citation - M25's boxes): since E65 the placer may put a card in the plot's own empty ROOM on purpose, so the plot box is the WARN tier and the ink is the FAIL. A PARKED card is E45's contract and M25's row. Read from the page's own DOM (probe.py --gate)
  [PASS ] M01 longest still stretch 1.6s at 0:57
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 27s from 0:09
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 7 distinct plates; target runtime/12s = 7
          doc 29 s9.13 plate density
  [PASS ] M05 1 plate(s) over the 20s hold, every one LIVE across it (worst gap 1.1s of 2.5s allowed)
          doc 29 s9.13 as amended by E69 (2026-09-12): the hold is legal while the FRAME LIVES - the ceiling's two-dock condition was written when a world was a still and only a card could move on it
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
  [PASS ] M16 longest gap between visual events 1.6s at 0:57; 0 gap(s) over 2.5s
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [PASS ] M23 6 transition(s), each on a built chart and clear of its page's edge: s02 rescale 0:21+1.4s, s02 park 0:36+0.9s, s04 park 0:54+0.9s, s04 recast 0:50+1.4s, s04 recast 0:56+0.5s, s04 park 0:59+0.9s
          P48 (operator 2026-09-07): chart-to-chart transitions are a first-rate feature - a chart changes STATE and never cuts; E45/E50: never over a build, never inside the last 0.5 s of a page's life
  [PASS ] M24 3 pointing species on moving-camera scenes, every target in frame when it fires
          P49 T6 (operator 2026-09-08: 'our engine ... doesn't know what it's seeing until it's rendered back'): a pointing species whose target is out of the camera's frame when it fires points at nothing - checked from the track before render
  [PASS ] M25 no settled card on the chart's data, on a line of the page's ink or in the caption strip over 64 instants probed; smallest type read 11.6 CSS px on a phone (floor 11) | INFO, listed not scored (CSS px on a phone): source parked 4.9, chart.lab parked 7.5, chart.bklab parked 8.1, chart.val parked 8.1
          E45 s1 (the compiler's `place`: a card parks in the page's quiet space, never over the plot, the title, the source line or the caption's anchor) / E52 (the page CITES: the citation rides the park) / E60 - the three defects of 2026-09-10, refused from the page's own DOM (probe.py --gate)
  [PASS ] M26 53 printed value(s) over 64 instants probed agree with the height drawn on the scale the page prints (band 4% of the top tick + the burst's 5% overshoot); worst 2.9% of the top tick - May at 0:56
          E28 (a chart reads right at a glance: a bar's height IS its value) / E53 (the scale and the value are printed at every instant) / R26-40 - the printed number and the DRAWN height, read against the scale the page itself prints, from the page's own DOM (probe.py --gate). R26-39 was exactly this mismatch: 303 px of bar at "0.00 %"
  [PASS ] M29 1 transient cue(s) inside the drop window, each with a page or dock landing on it: landing 2 (throw, paper) at 9.51s gain 0.12 with s02 dock dock-c-blue-ties-panel throw lands at 9.55s (window 0:05-0:12, E44 s2a: the press cue at a cut is not a hook device)
          E44 s2a / R26-5 (operator 2026-09-06: "the camera flash sound maybe shouldn't be as aggressive"): the press / flash cue at a cut is not a hook device - at 0:09 it is the last thing a viewer hears before leaving, so no TRANSIENT cue lands inside 0:05-0:12 unless a PAGE lands with it (the page's own arrival or its chart's landing, within 1.5 s). E83 (operator 2026-09-13: "for sound cue timing on docks: we probably should have sound cues"): a DOCK's own landing licenses the cue the same way - a card that lands is an instant the cue marks, not a cut's flash. The beds are exempt: a bed marks no instant
  [INFO ] M07 short: 1 full minute(s) in 89s - opening 220.0 events/min, 6.0 evidence entries/min; tail from 1:00 183.2/min; whole runtime 207.4/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M18 frozen frames not measured - run measure_frozen_frames.py <build> (writes frame-hashes.json)
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py); R26-13: read PER LAYER too - the page, the docks and the captions each on their own (frame-hashes.<layer>.json, the shell's ?layers= switch), because a caption boiling over a frozen page passes the whole-frame hash (Tokyo v2: 1036 distinct frames of 1066, M18 PASS, the pages still). The whole-frame verdict is still reported.
  [INFO ] M19 1 build_to hold(s) - the line rests at a datum until the next word: 0:07+11.5s
          P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness
  [INFO ] M20 3 arrival(s): dock-c-blue-ties-panel throw ~1311 px/s -> on 1s; dock-g-two-fingers land (metal) - weight sold 0.32s before the impact; dock-h-fed-vs-yields throw ~2336 px/s -> on 1s
          P47 T1 (the brief :185-193, the cadence rule): a throw steps on 1s above 250 px/s, on 2s below - reported, not scored, until HG2 tunes it
  [INFO ] M31 not measured - run measure_stage_gaps.py <build> to read the empty stage
          R26-66 / P53 T2, measured with measure_stage_gaps.py: a transition that TAKES the world (a suck, a melt) left the stage with no world on it for 3.1 s while the narration was already on the next sentence - 8.9% of a 69 s short. The DIP is the one transition licensed to empty the stage (a dip is a world change); everything else hands off, and the page that follows an inked arrival (enter=axes / built) measures 0.
  [INFO ] M32 not measured - run measure_seam_frames.py <build> to read the seams frame by frame
          P54 T9 (the operator, 2026-09-13: 'it's really the flash before or a second black frame that we're looking for'): measure_seam_frames.py seeks every boundary frame by frame; near-black = mean luma < 8 [MEASURED on the approved Japan short's six dips: darkest 0-6, cuts never under 52]. A declared dip's own dark core is the design; black anywhere else at a seam is the fault the operator found by hand twice (2026-09-05, 2026-09-12)
  [INFO ] M33 not measured - run measure_spoken_visuals.py <build>
          P54 T9 (the operator, 2026-09-13: 'gating for narration without the chart on screen is probably valid'; 2026-08-29: 'you open on the "spike" but you don't have the spike ons creen, you talk about charts without the charts on screen'): measure_spoken_visuals.py - a pointing phrase needs a page, a dock or a card on stage. WARN until the approved shorts show a real example (their one hit is a figure of speech)
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 2 FAIL / 3 WARN / 18 PASS / 1 JUDGE / 7 INFO
```

TIMELINE: tokyo-short.timeline.json sha256:5bec2d8ba4ccb230ef9d92322f5c51976ad12807652cecea7d659b2460f6cc22
VERDICT: FAIL (2 FAIL)
