# SCRIPT GATES - SCRIPT-VO.txt

script: SCRIPT-VO.txt
generated: 2026-09-19T21:18:28+00:00
script_hash: 3051887ec9c4554ded24751f9a6aaa1c32bfe8912a30d11833c127c77d2ba796
timing_source: estimated
form: long

TOOLS      lint: exit 1, 1 fails | audit: exit 1, 1/2, timing=estimated |
           opening gate: exit 1, 3/3/43/14 | screens: SCRIPT-SCREENS.md, 92 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

OPENING REVIEW: PASS (human draft review; measured timing still required)
opening_review: content\video_engine\projects\systems-and-blowups\fed-liquidity-pressure\SCRIPT-OPENING-REVIEW.json

## lint_script_pattern.py
exit 1

```
FAIL RING: no opening token recurs in the close
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 11.0, 'sentence_count': 190, 'word_count': 2095, 'rehook_positions_pct': []}
RESULT: 1 failure(s)
```

## audit_script_doctrine.py
exit 1

```
=== SCRIPT-VO.txt ===
             chars: 12388
         runtime_s: 748.0
           runtime: 12m 27s
         sentences: 190
     sentence_mean: 11.0
      break_ration: 0.16
  sentence_mean_carrying: 11.4
  short_figure_share: 4.7%
    sentence_stdev: 4.1
     over_20_share: 2.1%
       hook_spread: 10%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 3.9
       first_you_s: 22.7
         cta_count: 1
           rehooks: []
         phase_map: {'P1 OPEN': '0.0-1.5m', 'P2 ENGINE': '1.5-2.8m', 'P3 GAP': '2.1-5.6m', 'P4 PIVOT': '5.6-6.9m', 'P5 REFLECTION': '6.9-10.8m', 'P6 CLOSE': '11.0-12.5m'}
  p3_units_expected: 2
         a3_anchor: 1:14
         pivot_pct: 51.0
     timing_source: estimated (no take on disk)

  [FAIL] doc 35 rule 2: no falsifiable tell — an answer video must name one variable, one threshold, where we sit, and what flips us
  [WARN] MAP sec 2: no rehook construction within 45s of anchor(s) A1, A2, A3 (A1 ~0:30, A2 ~1:00, A3 ~1:14 at 12:27 = 10% of runtime) — found at none
  [WARN] doc 35 rule 2: the tell does not state what being wrong looks like
  [INFO] doc 37 sec 8: 12,388 chars exceeds the mv2 10,000 cap — chained take required, split at a phase boundary
  [INFO] estimator: the two rate estimates disagree by 10% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\fed-liquidity-pressure\SCRIPT-GATES.md

RESULT: 1 FAIL, 2 WARN
```

## gate_opening_structure.py
exit 1

```
=== OPENING STRUCTURE GATE: SCRIPT-VO.txt ===
           runtime: 12:15
            timing: estimated (kit rate, 8% band)
          geometry: P1 0:00-1:07 (beat 5 from 0:45), P2 -2:38 (phase guides)
     density_bands: loops (3, 4), new-info (5, 7)
         a3_anchor: 1:13
             cycle: checked 0:00-12:15; longest gap 49s from 5:27
      unit_windows: ['P3 unit 1 2:04-3:47', 'P3 unit 2 3:47-5:30', 'P5 unit 3 6:44-8:41', 'P5 unit 4 8:41-10:39']
      counterparty: net liquidity
              ring: machine
         packaging: title='The Hidden Fed Metric Breaking the Economy' thumb=None thumb_file=None
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'payoff': ['0:03', '3:19', '5:27', '7:35', '9:18', '11:06'], 'archetype': ['0:18'], 'stakes': ['0:20'], 'ring': ['0:28', '11:40'], 'tricolon': ['0:32', '11:46'], 'promise': ['0:36'], 'reflect': ['0:56', '2:56', '4:09', '6:16', '7:08', '9:40', '10:39'], 'opponent': ['0:56'], 'desire': ['1:07'], 'map': ['1:07'], 'rehook': ['1:13', '3:36', '4:14', '4:33', '6:23', '7:18', '8:59', '9:55', '11:02'], 'new': ['1:13', '1:19', '1:22', '1:41', '2:02', '2:27', '2:31', '3:39', '3:44', '4:21', '4:38', '6:27', '6:35', '6:47', '7:40', '7:48', '8:00', '8:06', '8:27', '10:02', '10:43'], 'catalyst': ['1:33'], 'foreshadow': ['1:33'], 'head-fake': ['1:52'], 'loop': ['2:19', '5:20'], 'debate': ['2:23'], 'loop-close': ['3:11'], 'signpost': ['3:11'], 'dip': ['3:16'], 'anaphora': ['11:46']}

  [FAIL ] G15b close shares 1 content stem(s) with the P1 claim (need 2); claim stems: ['work']
          Ring MECHANISM: the claim planted with the token in P1 recurs in the close (47 s2 G-g)
  [FAIL ] G21 1 [loop] in P2
          L2 loops: 3-4 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [FAIL ] G27 'machine' 0x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [WARN ] G31 0 dabs for 1 loops
          Glass alternation, P2 70/30: two loops with no reflection = listing (P2)
  [WARN ] G43 2/9 declared beats open on a gap/consequence connector
          McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)
  [WARN ] G48 1 publication-relative anchor(s) - re-screen each at publish and at any re-upload (a re-upload is a new assertion date): 10:48 'today' in 'For a business that needs a new loan, today’s borrowing cond'
          Perishable time anchors: every publication-relative phrase ('this week', 'last month', 'yesterday', 'two weeks ago', 'right now', 'this year') listed with its clock and re-screened at publish and at any re-upload - a false time anchor is the same class of defect as a false figure (C09-R013, ledger 8eb3d01c6196, 7e61f43b1162: 'a re-upload renews them at today's date.')
  [PASS ] G01 first sentence 2.33s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G03 paid at 3.90s, settle at 3.90s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:18
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:20
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:03
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G09 promise at 0:36
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G10 placed
          Humes pre-key immediately before the promise (P1 pause marks)
  [PASS ] G11 'You’ll leave with three checks you can run against public data to help'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G12 1 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [PASS ] G13 A1 at 0:36 ([promise]); A2 at 1:13 ([rehook])
          PLATFORM rehook slots A1 ~0:30 and A2 ~1:00 by FUNCTION, a line that re-justifies the next stretch: a declared [rehook] or [promise], the dated promise, a forward promise with a time or sequence anchor, or a template-family line - the families are one signal, not the definition (38 B4 / 38 B5 / P1 QC / MAP s3; C04-R016 + C07-R007, ledger b1f8c3fc2999: 'check the function doctrine specifies, not the phrasing it happens to illustrate')
  [PASS ] G14 [opponent] at 0:56
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [PASS ] G15 'machine' planted at 0:28
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [PASS ] G16 1 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 2 marks in P1 (1.8/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G19 closed by [loop] at 2:19
          The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)
  [PASS ] G20 longest gap 25s
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2)
  [PASS ] G22 7 [new] in P2
          PLATFORM density: 5-7 new-info beats at this runtime (P2 geometry)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G24 [head-fake] at 1:52
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [PASS ] G25 A3 at 1:13
          PLATFORM rehook A3 at ~10% of runtime = 1:13 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G26 [foreshadow] at 1:33
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [PASS ] G28 [loop-close] at 3:11
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [PASS ] G29 [dip] at 3:16
          PLATFORM breathing dip IMMEDIATELY after the macro close - 2-3 beats of room tone (P2)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G32 tricolon 0, anaphora P1 0 / P2 0
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 0 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G34 clean
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [PASS ] G35 clean
          U6 / E20: a delivered proof is never hedged in the next sentence
  [PASS ] G36 longest stretch without a cycle beat: 49s from 5:27
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-12:15 (E23: whole runtime)
  [PASS ] G37 [archetype] at 0:18
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [PASS ] G38 [desire] at 1:07
          Truby Desire named: the goal the video pursues (38 B5)
  [PASS ] G39 [map] at 1:07
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [PASS ] G40 [catalyst] at 1:33
          Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)
  [PASS ] G41 [debate] at 2:23
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [PASS ] G42 [signpost] at 3:11
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [PASS ] G44 all 4 unit windows rehook out
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [PASS ] G45 title-word proxy: ['fed'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] G46 runtime 12:15 (estimated) clears the 8:00 floor
          E74: long form is never under 8 minutes (the operator, 2026-09-13: 'yes, longform should never be under 8 minutes'; 2026-08-29: 'i dont think we make vdieos shorter than 8 minutes') - a cut under 8:00 is extended with substance or run as a short (under 3:00, G2), never shipped as a long form in between
  [PASS ] G47 no self-referential runtime claim
          A script's promises about itself: a self-referential runtime ('the next eight minutes', 'this ten-minute video') agrees with the clock within max(60 s, 15%) - FAIL on a measured take, WARN on the estimate; a deadline ('in the next N minutes') breaks only past the end (C03-R011, ledger e319a9d02fe4: 'The script promised eight minutes and ran twelve.')
  [PASS ] G47b 1 counted promise(s) agree with what the script names
          A script's promises about itself: a counted promise ('the five', 'three questions') agrees with the items the script names - the nearest named list, or the ordinals it walks - heuristic, so WARN (C03-R011, ledger e319a9d02fe4: 'A viewer counts four and then hears five.')
  [INFO ] G02 edit-clock property - checked with --timeline
          Humes pre-opener, bent visual: plate breathes 0.5-0.8s before the first word
  [JUDGE] J01 read the [opponent] line at 0:56
          McKee antagonism: the opponent is a mechanism, not a villain
  [JUDGE] J02 read the line at 1:52
          P2: the head-fake is offered STRAIGHT, no wink; demolition reserved for the pivot
  [JUDGE] J03 'The Fed’s balance fell by trillions.'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'The Fed’s balance fell by trillions.' -> 'Bank reserves barely budged.'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J09 read the line at 0:18
          McKee archetype, not stereotype: a universal experience in a specific setting (doc 32 s4)
  [JUDGE] J10 read the line at 1:07
          38 B5: the map is a journey tease, never a table of contents
  [JUDGE] J11 read the line at 2:23
          McKee: the plan fails as a GAP (an action whose result violates expectation), never as a lecture
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'The Fed’s balance fell by trillions.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J13 read the stakes line; record the human consequence, exact quote, and clock (by 0:30)
          Human-stakes read: by 0:30 the opening names a concrete human consequence (who is affected, what changes, and what is at risk); cite the spoken line and clock
  [JUDGE] J14 read the promise line; record the specific deliverable/test/source, exact quote, and clock (by 0:45)
          Useful-stay read: by 0:45 the opening promises a specific viewer-verifiable deliverable, test, check, or source; cite the spoken line and clock

RESULT: 3 FAIL / 3 WARN / 43 PASS / 14 JUDGE (read these) / 1 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-SCREENS.md: X1=27 deixis=15 junctions=3 anchors=47 declared=63
```

VERDICT: FAIL (3 failing tools)
