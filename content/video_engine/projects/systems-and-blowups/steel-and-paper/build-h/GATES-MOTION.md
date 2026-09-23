# MOTION GATE — build-h

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\fable-p68\content\video_engine\projects\systems-and-blowups\steel-and-paper\build-h ===
               runtime: 1:29
         visual_events: 257 (172.7/min)
   caption_page_events: 279 from 51 page(s) (42 anchor, 9 stage) + 228 word arrival(s) - the stage register plus the pages a full-stage row PINNED to the anchor (R26-232)
        live_page_life: 48 event(s) every 1.613s inside s01 0:00-0:42, s04 0:56-1:03, s05 1:03-1:29 - the PULSE rows M05/M10/M16 only (R26-232)
                 docks: 2
           dock_source: timeline
          ledger_pages: 3
  still_over_12s_share: 0%
            per_minute: 0:00:180/4 1:00:156/2

  [FAIL ] M03 longest wait for evidence to enter: 46s from 0:09
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [FAIL ] M11 first chart enters full and unannotated - declare a spotlight/callout/punch on its divergence within 1.5s AFTER the page's build lands at 4.8s (never over the build); window 0-10s (E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10)
          E24 / doc 29 s9.29 (long form) + E44 (short) + operator 2026-09-20: the first chart enters 0:08-0:20, 0:00-0:10 on a short, or 0:00-0:03 when explicitly authored as an opening ledger action; it is annotated on its divergence, with a sound cue
  [FAIL ] M31 1 chart-to-chart transition(s) leave empty cream on stage (1.0% of the runtime empty); worst s04 exit=melt 0.2s at 1:03 - the next page belongs on its axes under the outgoing one (stamp_transition_pages)
          R26-66 / P53 T2, measured with measure_stage_gaps.py: a transition that TAKES the world (a suck, a melt) left the stage with no world on it for 3.1 s while the narration was already on the next sentence - 8.9% of a 69 s short. The DIP is the one transition licensed to empty the stage (a dip is a world change); everything else hands off, and the page that follows an inked arrival (enter=axes / built) measures 0.
  [WARN ] M04 5 distinct plates; target runtime/12s = 7
          doc 29 s9.13 plate density
  [WARN ] M25 2 safe-zone intrusion(s) over 28 instants probed: a card is 19 % inside the bottom safe-zone band at 0:09; a card is 18 % inside the bottom safe-zone band at 0:10
          E45 s1 (the compiler's `place`: a card parks in the page's quiet space, never over the plot, the title, the source line or the caption's anchor) / E52 (the page CITES: the citation rides the park) / E60 - the three defects of 2026-09-10, refused from the page's own DOM (probe.py --gate)
  [PASS ] M01 longest still stretch 1.6s at 1:02
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M05 2 plate(s) over the 20s hold, every one LIVE across it (worst gap 1.4s of 2.5s allowed)
          doc 29 s9.13 as amended by E69 (2026-09-12): the hold is legal while the FRAME LIVES - the ceiling's two-dock condition was written when a world was a still and only a card could move on it. E99 s69 (2026-09-17): the liveness reads the same allowance as M16 - a dead stretch that starts at a page's chart landing and runs no longer than 4s is the chart's own hold, not a dead frame. R26-232 (2026-09-18): a live page's own life is a sustained event every 1.613s inside its span (R26-228's 0.62 Hz lead-point spark), and a caption page a full-stage row pinned to the anchor counts exactly as a stage page does - the row names the term
  [PASS ] M06 51 caption pages = 34/min, 4.5 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M08 timeline declares cap_mode; every stretch over the ceiling carries captions (counted as events above); counted: 42 anchor, 9 stage page(s), 228 word arrival(s)
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
  [PASS ] M16 longest gap between visual events 1.5s at 0:51; 0 gap(s) over 2.5s
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling. E99 s69 (2026-09-17): the HELD-BUILT window is exempt - a gap that starts at a page's chart LANDING and runs no longer than 4s is the beat's punctuation, not a hole (E99 s67 asked for that hold; HG2 may move the number). R26-232 (2026-09-18): a caption page a full-stage 16:9 page row PINNED to the anchored strip counts as a stage page does (R26-205), and inside the span of a page whose resolved idle is `live` (R26-228) the page's own life is an event every 1.613s - the period of the lead point's measured 0.62 Hz spark; the row names the term that fired
  [PASS ] M18 no run of bit-identical frames over 0.50s (824 frames at 12 fps, 0:00-1:08); longest 0.00s at 0:00
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py); R26-13: read PER LAYER too - the page, the docks and the captions each on their own (frame-hashes.<layer>.json, the shell's ?layers= switch), because a caption boiling over a frozen page passes the whole-frame hash (Tokyo v2: 1036 distinct frames of 1066, M18 PASS, the pages still). The whole-frame verdict is still reported.
  [PASS ] M23 2 transition(s), each on a built chart and clear of its page's edge: s01 rescale 0:28+2.2s, s05 recast 1:20+2.0s; s01 rescale at 0:28 FOLLOWS its line - on the line's own clock, so the over-a-build check does not apply to it (R26-233)
          P48 (operator 2026-09-07): chart-to-chart transitions are a first-rate feature - a chart changes STATE and never cuts; E45/E50: never over a build, never inside the last 0.5 s of a page's life. R26-233 (2026-09-18): a `chart_to rescale` that carries `follow` is EXEMPT from the over-a-build check - a followed rescale runs on the followed LINE's own clock (the domain's top is that series' drawn extremum frame by frame, `build_scene_timeline_f.py:3796`), so the line's `build_to` IS its clock and "over the build" is the shape the move is FOR (the breakthrough bars' shape on a line page). The edge check still binds.
  [PASS ] M24 1 pointing species on moving-camera scenes, every target in frame when it fires
          P49 T6 (operator 2026-09-08: 'our engine ... doesn't know what it's seeing until it's rendered back'): a pointing species whose target is out of the camera's frame when it fires points at nothing - checked from the track before render
  [PASS ] M27 no card reads over a ledger page's ink over 28 instants probed (4 not-parked card reading(s) measured)
          E63 (operator 2026-09-11, on the Tokyo cut at 0:09.5-0:10.5: "docking over the plate while it's drawing is not a good standard practice ... as a rule we should probably use better handling now that we can manipulate scale/depth/placement easier"; widened the same evening, on the read that came back over the finished chart: "im confused, because you just left the dock over the chart now too. something went backwards"): a card that has not parked yet may not sit on a ledger page's INK, drawing or finished - the READ moves (the compiler's `read_moved` / `read_deferred`), never the word. The page's own INK is what the row scores (the data, the labels, the citation - M25's boxes): since E65 the placer may put a card in the plot's own empty ROOM on purpose, so the plot box is the WARN tier and the ink is the FAIL. A PARKED card is E45's contract and M25's row. Read from the page's own DOM (probe.py --gate)
  [PASS ] M28 no two of a page's own labels touch, and the value row keeps half a figure of air, over 28 instants probed (1,066 label pair(s) checked)
          R26-53 (the operator, 2026-09-11: "why are we now crashing text?") - the Tokyo Meta page's four values "$665 $633 $604 $577" touched each other and the callout's pill on bar 4 covered bar 3's label, on the approved build and on every side build before f67c5ed, and no row saw it: M25 reads cards over ink, M26 the value's height, and the probe's `overlaps` carried card-vs-ink and pill-vs-rail only. E28 (a chart reads right at a glance): no two of a page's OWN labels may sit on each other, and the row that fits them (lpFitValues / lpPillBand) leaves half a figure of air between them. From the page's own DOM (probe.py --gate)
  [PASS ] M29 1 transient cue(s) inside the drop window, each with a page or dock landing on it: landing 1 (throw, paper) at 9.62s gain 0.12 with s01 dock dock-h-certificate-1845 throw lands at 9.66s (window 0:05-0:12, E44 s2a: the press cue at a cut is not a hook device)
          E44 s2a / R26-5 (operator 2026-09-06: "the camera flash sound maybe shouldn't be as aggressive"): the press / flash cue at a cut is not a hook device - at 0:09 it is the last thing a viewer hears before leaving, so no TRANSIENT cue lands inside 0:05-0:12 unless a PAGE lands with it (the page's own arrival or its chart's landing, within 1.5 s). E83 (operator 2026-09-13: "for sound cue timing on docks: we probably should have sound cues"): a DOCK's own landing licenses the cue the same way - a card that lands is an instant the cue marks, not a cut's flash. The beds are exempt: a bed marks no instant
  [PASS ] M32 4 boundaries read frame by frame: no flash, no jump, no black outside a dip's core
          P54 T9 (the operator, 2026-09-13: 'it's really the flash before or a second black frame that we're looking for'): measure_seam_frames.py seeks every boundary frame by frame; near-black = mean luma < 8 [MEASURED on the approved Japan short's six dips: darkest 0-6, cuts never under 52]. A declared dip's own dark core is the design; black anywhere else at a seam is the fault the operator found by hand twice (2026-09-05, 2026-09-12)
  [PASS ] M33 1 pointing phrase(s), each with a page, dock or card on stage
          P54 T9 (the operator, 2026-09-13: 'gating for narration without the chart on screen is probably valid'; 2026-08-29: 'you open on the "spike" but you don't have the spike ons creen, you talk about charts without the charts on screen'): measure_spoken_visuals.py - a pointing phrase needs a page, a dock or a card on stage. WARN until the approved shorts show a real example (their one hit is a figure of speech)
  [PASS ] M44 every world plate holds at least 6s (2 world plate(s), floor 6s)
          sub-6s-plate (the operator, 2026-08-29, ledger 69ff558bdf67; docs/operator-ledger/TRIAGE-DIGEST.md: "the baloon dock doesn't even make sense ... why do we have a plate less than 6 seconds long?"): a world plate under 6 s is a flash the eye cannot take in, and one that also carries a DOCK asks the eye to read evidence inside that flash. BUILD-PIPELINE says only "under ~8s one piece or none" and nothing checked plate length. Read from the timeline's own scenes - no browser, no render
  [INFO ] M07 short: 1 full minute(s) in 89s - opening 180.0 events/min, 4.0 evidence entries/min; tail from 1:00 155.8/min; whole runtime 171.4/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M19 4 build_to hold(s) - the line rests at a datum until the next word: 0:00+27.8s, 1:04+1.1s, 1:14+3.0s, 1:18+7.8s
          P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness
  [INFO ] M20 2 arrival(s): dock-h-certificate-1845 throw ~1103 px/s -> on 1s; dock-h-two-line-copy throw ~2016 px/s -> on 1s
          P47 T1 + E99 s30 (the cadence rule, cinema parity): a throw steps on 1s above 154 px/s, on 2s below - reported, not scored, until HG2 tunes it
  [INFO ] M21 1 page(s) deployed 8-12s after the last data mark (a dock's clip may hold it): s01 11.6s (0:30 -> 0:42)
          E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing
  [INFO ] M26 no bars page printed a value at any of the 28 instants probed - nothing to check (a line page's numbers are its tags, not a height)
          E28 (a chart reads right at a glance: a bar's height IS its value) / E53 (the scale and the value are printed at every instant) / R26-40 - the printed number and the DRAWN height, read against the scale the page itself prints, from the page's own DOM (probe.py --gate). R26-39 was exactly this mismatch: 303 px of bar at "0.00 %"
  [INFO ] M34 no text box met a mark or a series line at any of the 28 instants probed - nothing to check
          K9, the operator's reasoning items C05-R023 ("every text element must be in the collision ledger, including the ones that were already there"; "labels are all crashing with the lines") and C09-R003 ("the callout owns its position"; measure the rendered boxes, never estimate), and the two defects no row caught on normal-for-which-bridge review-v1 (docs/agent-memory/operator/casebook/ring-on-the-tip-label: the dashed 123% ring painted over "x3.9 Federal debt" at 0:57; .../name-on-the-neighbour-line: "10-year" written across the 30-year line at 0:19, the 4.83% arc clipping it). M28 pairs labels with labels; this row puts every text box against every mark's stroke and every series polyline, from the page's own DOM (probe.py --gate). The operator, 2026-09-13: "bracket should probably be able to bypass that rule" - a bracket's or a figure's own text on the series it measures is allowed (on a DIFFERENT series' line it still FAILs); and "a ring or callout drawn over a label doesn't automatically fail, if the point is to draw a ring or highlight around that label - but we have spotlight tools that can provide more clarity while demanding less accuracy" - a mark over its OWN target's text (the datum it rings: a bar's value, its pill, a figure or bracket at that datum) WARNs and names the spotlight (E56: a ring circles a number or a point on a chart); over any other text it FAILs
  [INFO ] M43 1 camera landing(s), none with an identity-camera probe instant within 1.5s on its own scene - add those instants to probe.py --gate
          punch-crops-text (the operator, 2026-09-03, ledger 16d1b9558a10; docs/operator-ledger/TRIAGE-DIGEST.md): a text box the camera's landed frame cuts PARTWAY is a cropped word. Fully inside reads, fully outside is a choice the author made; half of a sentence hanging off the frame edge is neither. The frame is the frustum M24 computes from the row's own camera (camera_state_at + camera_frustum); the boxes are probe.py --gate's (layout-probe.json), the file M25/M26/M27/M28/M34 already read
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 3 FAIL / 2 WARN / 20 PASS / 1 JUDGE / 7 INFO
```

TIMELINE: steel-and-paper-h.timeline.json sha256:3da603cfca2854d46f813b802a9f2d64c20a34fd54866679aa99f7812cbe81e7
VERDICT: FAIL (3 FAIL)
