# MOTION GATE — pilot-sentence-response-v2

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\american-debt-trap\build-private\v15\pilot-sentence-response-v2 ===
               runtime: 2:57
         visual_events: 527 (177.7/min)
   caption_page_events: 615 from 109 page(s) (19 anchor, 90 stage) + 506 word arrival(s) - the stage register plus the pages a full-stage row PINNED to the anchor (R26-232)
        live_page_life: 21 event(s) every 1.613s inside s01 0:00-0:03, s10 1:21-1:26, s11 1:26-1:33, s12 1:33-1:42 - the PULSE rows M05/M10/M16 only (R26-232)
                 docks: 0
           dock_source: evidence-dock.json
          ledger_pages: 5
  still_over_12s_share: 0%
            per_minute: 0:00:183/1 1:00:165/4 2:00:184/0

  [FAIL ] M03 longest wait for evidence to enter: 82s from 0:00 (no docks at all)
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [WARN ] M11 first chart ledger:s01 enters at 0.0s, its build lands at 3.0s, with spotlight at 3.0s; WARN no sound cue within 1.5s of the enter at 0.0s (no evidence species in the timeline - every dock treated as a chart candidate); window 0-3s (operator-directed long-form cold open: the ledger is the opening action by 0:03)
          E24 / doc 29 s9.29 (long form) + E44 (short) + operator 2026-09-20: the first chart enters 0:08-0:20, 0:00-0:10 on a short, or 0:00-0:03 when explicitly authored as an opening ledger action; it is annotated on its divergence, with a sound cue
  [WARN ] M23 1 transition(s): s12 compare 1:40+2.4s - s12 compare at 1:40 ends inside the last 0.5 s of its page (E45: never over a build; E50: a transition is how a chart leaves, not a cut wearing a verb)
          P48 (operator 2026-09-07): chart-to-chart transitions are a first-rate feature - a chart changes STATE and never cuts; E45/E50: never over a build, never inside the last 0.5 s of a page's life. R26-233 (2026-09-18): a `chart_to rescale` that carries `follow` is EXEMPT from the over-a-build check - a followed rescale runs on the followed LINE's own clock (the domain's top is that series' drawn extremum frame by frame, `build_scene_timeline_f.py:3796`), so the line's `build_to` IS its clock and "over the build" is the shape the move is FOR (the breakthrough bars' shape on a line page). The edge check still binds.
  [PASS ] M01 longest still stretch 1.5s at 1:45
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M04 16 distinct plates; target runtime/12s = 14
          doc 29 s9.13 plate density
  [PASS ] M05 1 plate(s) over the 20s hold, every one LIVE across it (worst gap 1.1s of 8.0s allowed)
          doc 29 s9.13 as amended by E69 (2026-09-12): the hold is legal while the FRAME LIVES - the ceiling's two-dock condition was written when a world was a still and only a card could move on it. E99 s69 (2026-09-17): the liveness reads the same allowance as M16 - a dead stretch that starts at a page's chart landing and runs no longer than 4s is the chart's own hold, not a dead frame. R26-232 (2026-09-18): a live page's own life is a sustained event every 1.613s inside its span (R26-228's 0.62 Hz lead-point spark), and a caption page a full-stage row pinned to the anchor counts exactly as a stage page does - the row names the term
  [PASS ] M06 109 caption pages = 37/min, 4.6 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M08 timeline declares cap_mode; every stretch over the ceiling carries captions (counted as events above); counted: 19 anchor, 90 stage page(s), 506 word arrival(s)
          doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves). R26-232 (1) (2026-09-18): a caption page is an event wherever the PAGE puts it - a page a full-stage 16:9 page row PINNED to the anchored strip (R26-205) counts exactly as a stage page does, because there the anchor is the only register the player can paint; a lower-third page over a plate the page does not own counts as nothing still (E21, episode one's verdict - the cut this row is calibrated on)
  [PASS ] M09 no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns
          doc 29 s9.27 precedence / s9.28 C3: one camera move per window
  [PASS ] M10 no still stretch > 6s begins in the first 60s
          E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s. R26-232 (2026-09-18): the opening's stillness is read with the same two terms as M05 and M16 - a caption page pinned to the anchor by a full-stage page row counts as a stage page does, and a live page's own life is an event every 1.613s inside its span (R26-228)
  [PASS ] M12 no chart dock spans a scene boundary or holds past 10s (6s in the opening minute)
          E25 / doc 29 s9.30: the chart is the proof, not the homework
  [PASS ] M14 no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal
          47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move
  [PASS ] M15 no species window overlaps a page's retract
          E40 #5 (operator, 2026-09-05): no spotlight on a spiral out - no species window overlaps a page's retract
  [PASS ] M21 every ledger page leaves or un-draws within 8s of its last data mark: s01 0.4s (0:03 -> 0:03); s10 2.1s (1:24 -> 1:26); s11 4.2s (1:29 -> 1:33); s12 5.9s (1:36 -> 1:42); s15 1.8s (2:00 -> 2:02)
          E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing
  [PASS ] M24 0 pointing species on moving-camera scenes, every target in frame when it fires
          P49 T6 (operator 2026-09-08: 'our engine ... doesn't know what it's seeing until it's rendered back'): a pointing species whose target is out of the camera's frame when it fires points at nothing - checked from the track before render
  [PASS ] M44 every world plate holds at least 6s (14 world plate(s), floor 6s)
          sub-6s-plate (the operator, 2026-08-29, ledger 69ff558bdf67; docs/operator-ledger/TRIAGE-DIGEST.md: "the baloon dock doesn't even make sense ... why do we have a plate less than 6 seconds long?"): a world plate under 6 s is a flash the eye cannot take in, and one that also carries a DOCK asks the eye to read evidence inside that flash. BUILD-PIPELINE says only "under ~8s one piece or none" and nothing checked plate length. Read from the timeline's own scenes - no browser, no render
  [INFO ] M07 short: 2 full minute(s) in 178s - opening 183.0 events/min, 1.0 evidence entries/min; tail from 1:00 165.0/min; whole runtime 177.0/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M16 longest gap between visual events 1.5s at 1:45; 0 gap(s) over 2.5s - a long-form build; the pulse law binds shorts
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling. E99 s69 (2026-09-17): the HELD-BUILT window is exempt - a gap that starts at a page's chart LANDING and runs no longer than 4s is the beat's punctuation, not a hole (E99 s67 asked for that hold; HG2 may move the number). R26-232 (2026-09-18): a caption page a full-stage 16:9 page row PINNED to the anchored strip counts as a stage page does (R26-205), and inside the span of a page whose resolved idle is `live` (R26-228) the page's own life is an event every 1.613s - the period of the lead point's measured 0.62 Hz spark; the row names the term that fired
  [INFO ] M18 frozen frames not measured - run measure_frozen_frames.py <build> (writes frame-hashes.json)
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py); R26-13: read PER LAYER too - the page, the docks and the captions each on their own (frame-hashes.<layer>.json, the shell's ?layers= switch), because a caption boiling over a frozen page passes the whole-frame hash (Tokyo v2: 1036 distinct frames of 1066, M18 PASS, the pages still). The whole-frame verdict is still reported.
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
  [INFO ] M43 1 camera landing(s) unmeasured - run probe.py <build> --gate (writes layout-probe.json)
          punch-crops-text (the operator, 2026-09-03, ledger 16d1b9558a10; docs/operator-ledger/TRIAGE-DIGEST.md): a text box the camera's landed frame cuts PARTWAY is a cropped word. Fully inside reads, fully outside is a choice the author made; half of a sentence hanging off the frame edge is neither. The frame is the frustum M24 computes from the row's own camera (camera_state_at + camera_frustum); the boxes are probe.py --gate's (layout-probe.json), the file M25/M26/M27/M28/M34 already read
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 1 FAIL / 2 WARN / 14 PASS / 1 JUDGE / 11 INFO
```

TIMELINE: american-debt-trap-v15-pilot.timeline.json sha256:4fb7ecf06703a5de015fe5001b87b912740fdfdcf2a31a6fc44ecdd0bea77e11
VERDICT: FAIL (1 FAIL)
