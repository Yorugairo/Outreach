# G20 advisory recheck

Operator-directed policy change, 2026-09-20. Original V13 FAIL report retained.
Frozen narration unchanged. Regression tests: 3 passed. Exit code: 0.
This report covers the opening-structure checker, not final release approval.

```text
=== OPENING STRUCTURE GATE: REVISED-V13-VO.txt ===
           runtime: 9:01
            timing: estimated (kit rate, 8% band)
          geometry: P1 0:00-1:01 (beat 5 from 0:41), P2 -2:20 (phase guides)
     density_bands: loops (2, 3), new-info (4, 6)
         a3_anchor: 0:54
             cycle: checked 0:00-9:01; longest gap 57s from 6:12
      unit_windows: ['P3 unit 1 1:32-4:03', 'P5 unit 2 4:57-7:51']
      counterparty: refinancing
              ring: renewal letter
         packaging: title='Inside the Great American Debt Trap: How It Becomes Your Problem' thumb=None thumb_file=None
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'archetype': ['0:09'], 'stakes': ['0:17'], 'payoff': ['0:25', '3:28', '4:21', '5:19', '5:54', '7:33'], 'reflect': ['0:25', '1:54'], 'promise': ['0:29'], 'desire': ['0:44'], 'opponent': ['0:47'], 'ring': ['0:51', '8:33'], 'map': ['0:55'], 'rehook': ['0:55', '2:42', '3:58', '4:57', '6:12', '7:09'], 'foreshadow': ['0:55', '3:41'], 'tricolon': ['1:00'], 'head-fake': ['1:15'], 'catalyst': ['1:29'], 'new': ['1:35', '1:40', '1:59', '2:17'], 'loop': ['1:45', '2:12'], 'debate': ['2:27'], 'loop-close': ['2:30', '8:09'], 'dip': ['2:34'], 'signpost': ['2:37']}

  [WARN ] G20 longest gap 34s; review information gain against narration
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2; advisory)
  [WARN ] G43 0/7 declared beats open on a gap/consequence connector
          McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)
  [PASS ] G01 first sentence 2.66s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G03 paid at 6.71s, settle at 6.71s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:00
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:17
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:25
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G09 promise at 0:29
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G10 placed
          Humes pre-key immediately before the promise (P1 pause marks)
  [PASS ] G11 'Stay for three checks you can run against public data to help protect '
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G12 1 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [PASS ] G13 A1 at 0:29 ([promise]); A2 at 0:55 ([rehook])
          PLATFORM rehook slots A1 ~0:30 and A2 ~1:00 by FUNCTION, a line that re-justifies the next stretch: a declared [rehook] or [promise], the dated promise, a forward promise with a time or sequence anchor, or a template-family line - the families are one signal, not the definition (38 B4 / 38 B5 / P1 QC / MAP s3; C04-R016 + C07-R007, ledger b1f8c3fc2999: 'check the function doctrine specifies, not the phrasing it happens to illustrate')
  [PASS ] G14 [opponent] at 0:47
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [PASS ] G15 'renewal letter' planted at 0:51
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [PASS ] G15b close shares 2 content stem(s) with the P1 claim (need 2); claim stems: ['afford', 'busines', 'chang', 'whole']
          Ring MECHANISM: the claim planted with the token in P1 recurs in the close (47 s2 G-g)
  [PASS ] G16 1 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 2 marks in P1 (1.9/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G19 closed by [loop] at 1:45
          The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)
  [PASS ] G21 2 [loop] in P2
          L2 loops: 2-3 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [PASS ] G22 4 [new] in P2
          PLATFORM density: 4-6 new-info beats at this runtime (P2 geometry)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G24 [head-fake] at 1:15
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [PASS ] G25 A3 at 0:55
          PLATFORM rehook A3 at ~10% of runtime = 0:54 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G26 [foreshadow] at 0:55
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [PASS ] G27 'renewal letter' 1x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [PASS ] G28 [loop-close] at 2:30
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [PASS ] G29 [dip] at 2:34
          PLATFORM breathing dip IMMEDIATELY after the macro close - 2-3 beats of room tone (P2)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G31 1 dabs, 2 loops
          Glass alternation, P2 70/30: dabs marked, never consecutive (P2)
  [PASS ] G32 tricolon 1, anaphora P1 0 / P2 0
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 0 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G34 clean
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [PASS ] G35 clean
          U6 / E20: a delivered proof is never hedged in the next sentence
  [PASS ] G36 longest stretch without a cycle beat: 57s from 6:12
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-9:01 (E23: whole runtime)
  [PASS ] G37 [archetype] at 0:09
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [PASS ] G38 [desire] at 0:44
          Truby Desire named: the goal the video pursues (38 B5)
  [PASS ] G39 [map] at 0:55
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [PASS ] G40 [catalyst] at 1:29
          Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)
  [PASS ] G41 [debate] at 2:27
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [PASS ] G42 [signpost] at 2:37
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [PASS ] G44 all 2 unit windows rehook out
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [PASS ] G45 title-word proxy: ['american', 'debt', 'trap'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] G46 runtime 9:01 (estimated) clears the 8:00 floor
          E74: long form is never under 8 minutes (the operator, 2026-09-13: 'yes, longform should never be under 8 minutes'; 2026-08-29: 'i dont think we make vdieos shorter than 8 minutes') - a cut under 8:00 is extended with substance or run as a short (under 3:00, G2), never shipped as a long form in between
  [PASS ] G47 no self-referential runtime claim
          A script's promises about itself: a self-referential runtime ('the next eight minutes', 'this ten-minute video') agrees with the clock within max(60 s, 15%) - FAIL on a measured take, WARN on the estimate; a deadline ('in the next N minutes') breaks only past the end (C03-R011, ledger e319a9d02fe4: 'The script promised eight minutes and ran twelve.')
  [PASS ] G47b 1 counted promise(s) agree with what the script names
          A script's promises about itself: a counted promise ('the five', 'three questions') agrees with the items the script names - the nearest named list, or the ordinals it walks - heuristic, so WARN (C03-R011, ledger e319a9d02fe4: 'A viewer counts four and then hears five.')
  [PASS ] G48 no publication-relative time anchor
          Perishable time anchors: every publication-relative phrase ('this week', 'last month', 'yesterday', 'two weeks ago', 'right now', 'this year') listed with its clock and re-screened at publish and at any re-upload - a false time anchor is the same class of defect as a false figure (C09-R013, ledger 8eb3d01c6196, 7e61f43b1162: 'a re-upload renews them at today's date.')
  [INFO ] G02 edit-clock property - checked with --timeline
          Humes pre-opener, bent visual: plate breathes 0.5-0.8s before the first word
  [JUDGE] J01 read the [opponent] line at 0:47
          McKee antagonism: the opponent is a mechanism, not a villain
  [JUDGE] J02 read the line at 1:15
          P2: the head-fake is offered STRAIGHT, no wink; demolition reserved for the pivot
  [JUDGE] J03 'America's debt trap can cost you a raise.'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'America's debt trap can cost you a raise.' -> 'Your employer can make every payment and still can'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J09 read the line at 0:09
          McKee archetype, not stereotype: a universal experience in a specific setting (doc 32 s4)
  [JUDGE] J10 read the line at 0:55
          38 B5: the map is a journey tease, never a table of contents
  [JUDGE] J11 read the line at 2:27
          McKee: the plan fails as a GAP (an action whose result violates expectation), never as a lecture
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'America's debt trap can cost you a raise.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J13 read the stakes line; record the human consequence, exact quote, and clock (by 0:30)
          Human-stakes read: by 0:30 the opening names a concrete human consequence (who is affected, what changes, and what is at risk); cite the spoken line and clock
  [JUDGE] J14 read the promise line; record the specific deliverable/test/source, exact quote, and clock (by 0:45)
          Useful-stay read: by 0:45 the opening promises a specific viewer-verifiable deliverable, test, check, or source; cite the spoken line and clock

RESULT: 0 FAIL / 2 WARN / 47 PASS / 14 JUDGE (read these) / 1 INFO

```

