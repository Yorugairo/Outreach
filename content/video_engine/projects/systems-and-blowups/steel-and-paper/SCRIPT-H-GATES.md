# SCRIPT GATES - SCRIPT-H-VO.txt

script: SCRIPT-H-VO.txt
generated: 2026-09-18T10:36:20+00:00
script_hash: 0582cfff9c850200268660d6a71f9a4d956bf8d99b26c91f597e4e6a4b91b8b8
timing_source: measured

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/0, timing=estimated |
           opening gate: exit 0, 0/3/47/12 | screens: SCRIPT-H-SCREENS.md, 177 items

VIEWER     SCRIPT-H-VIEWER.md  (advisory: --no-viewer-gate - these rows do not change the VERDICT)
  [INFO ] V01 45/52 declared beats perceived (87%); unperceived: [payoff] w2, [debate] w9, [loop] w9, [signpost] w10, [anaphora] w11, [anaphora] w24, [rehook] w32
  [INFO ] V04 2 window(s) with something unfollowable: 8:45-9:00 Who or what Bravos is; 13:30-13:45 The phrase about “Bravos at five and a half” and “mine on me
  [INFO ] V02 no run of 2+ windows without a concrete new thing
  [INFO ] V03 open loop live in 55/56 windows (98%)
  [INFO ] V05 gain per window: median 3, 0 dead of 56 reported

## lint_script_pattern.py
exit 0

```
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 11.2, 'sentence_count': 211, 'word_count': 2353, 'rehook_positions_pct': []}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-H-VO.txt ===
             chars: 13418
         runtime_s: 826.1
           runtime: 13m 46s
         sentences: 211
     sentence_mean: 11.2
      break_ration: 0.45
  sentence_mean_carrying: 12.4
  short_figure_share: 13.7%
    sentence_stdev: 5.9
     over_20_share: 6.6%
       hook_spread: 23%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 3.1
       first_you_s: 17.3
         cta_count: 1
           rehooks: ['2.2m', '7.1m']
         phase_map: {'P1 OPEN': '0.0-1.5m', 'P2 ENGINE': '1.5-3.0m', 'P3 GAP': '2.3-6.2m', 'P4 PIVOT': '6.2-7.6m', 'P5 REFLECTION': '7.6-12.0m', 'P6 CLOSE': '12.3-13.8m'}
  p3_units_expected: 2
         a3_anchor: 1:22
         pivot_pct: None
     timing_source: estimated (a take exists but is of DIFFERENT text — not used)

  [INFO] doc 37 sec 8: 13,418 chars exceeds the mv2 10,000 cap — chained take required, split at a phase boundary
  [INFO] estimator: the two rate estimates disagree by 23% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\steel-and-paper\SCRIPT-H-GATES.md

RESULT: 0 FAIL, 0 WARN
```

## gate_opening_structure.py
exit 0

```
=== OPENING STRUCTURE GATE: SCRIPT-H-VO.txt ===
           runtime: 13:58
            timing: measured (take)
          geometry: P1 0:00-1:11 (beat 5 from 0:47), P2 -2:48 (phase guides)
     density_bands: loops (3, 4), new-info (5, 7)
         a3_anchor: 1:23
             cycle: checked 0:00-13:58; longest gap 55s from 12:22
      unit_windows: ['P3 unit 1 2:22-4:19', 'P3 unit 2 4:19-6:17', 'P5 unit 3 7:41-9:55', 'P5 unit 4 9:55-12:09']
      counterparty: Bravos Research
              ring: certificate
         packaging: title='The AI Bubble Is Real. What Survives Is Steel.' thumb=None thumb_file=content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/thumbnail-FINAL-steelpaper.png
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'ring': ['0:00', '7:05', '11:47'], 'tricolon': ['0:04'], 'stakes': ['0:09'], 'archetype': ['0:21'], 'payoff': ['0:29'], 'reflect': ['0:40'], 'promise': ['0:44'], 'desire': ['0:51'], 'map': ['0:55'], 'opponent': ['0:57'], 'rehook': ['1:06', '4:14', '5:37', '8:01', '9:53', '10:29', '11:30', '12:22'], 'foreshadow': ['1:14', '6:31'], 'new': ['1:23', '1:29', '1:39', '1:52', '2:00', '2:07', '2:35', '3:05', '3:45', '4:31', '5:19', '5:42', '9:22'], 'catalyst': ['1:29'], 'loop': ['1:29', '2:14', '2:19'], 'head-fake': ['1:33'], 'debate': ['2:19'], 'loop-close': ['2:28'], 'dip': ['2:35'], 'signpost': ['2:38', '6:17', '10:54'], 'anaphora': ['2:46', '6:09', '8:44', '13:17'], 'turn': ['3:26'], 'concede': ['4:00']}

  [WARN ] G31 0 dabs for 3 loops
          Glass alternation, P2 70/30: two loops with no reflection = listing (P2)
  [WARN ] G43 2/9 declared beats open on a gap/consequence connector
          McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)
  [WARN ] G48 14 publication-relative anchor(s) - re-screen each at publish and at any re-upload (a re-upload is a new assertion date): 0:17 'today' in 'Hold an index fund and you own both halves today.'; 1:14 'today' in 'Railways in the 1840s drew a quarter-billion pounds, more th'; 3:09 'Today' in 'Today it's twenty-eight, the most it has ever been.'; 4:37 'Last year' in 'Last year: a hundred and twenty-one billion.'; 4:40 'This year' in 'This year they're tracking toward a hundred and fifty.'; 6:40 'today' in 'And Bravos Research's own number tells you where that paper '; 7:33 'Today' in 'Today's compute doesn't sit.'; 7:37 'next year' in 'And the builders are already sold out into next year — the o'; 8:17 'tonight' in 'Three: if the hype died tonight, would the asset still get u'; 8:17 'tomorrow' in 'Three: if the hype died tonight, would the asset still get u'; 8:52 'tonight' in 'Run your top five tonight.'; 9:22 'last year' in 'Over the last year the stock is up more than five hundred pe'; 9:49 'this year' in 'That's why the memory in a new laptop costs what it does thi'; 10:06 'tomorrow' in 'Used tomorrow morning?'
          Perishable time anchors: every publication-relative phrase ('this week', 'last month', 'yesterday', 'two weeks ago', 'right now', 'this year') listed with its clock and re-screened at publish and at any re-upload - a false time anchor is the same class of defect as a false figure (C09-R013, ledger 8eb3d01c6196, 7e61f43b1162: 'a re-upload renews them at today's date.')
  [PASS ] G01 first sentence 1.71s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G02 first word at 0.33s in the edit clock
          Humes pre-opener, bent visual: the plate breathes 0.5-0.8s before the first word (38 B1 / doc 32 s7)
  [PASS ] G03 paid at 3.58s, settle at 7.00s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:17
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:09
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:29
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G09 promise at 0:44
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G10 placed
          Humes pre-key immediately before the promise (P1 pause marks)
  [PASS ] G11 'One test, three questions, thirty seconds a holding, and it sorts ever'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G12 1 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [PASS ] G13 A1 at 0:44 ([promise]); A2 at 1:06 ([rehook])
          PLATFORM rehook slots A1 ~0:30 and A2 ~1:00 by FUNCTION, a line that re-justifies the next stretch: a declared [rehook] or [promise], the dated promise, a forward promise with a time or sequence anchor, or a template-family line - the families are one signal, not the definition (38 B4 / 38 B5 / P1 QC / MAP s3; C04-R016 + C07-R007, ledger b1f8c3fc2999: 'check the function doctrine specifies, not the phrasing it happens to illustrate')
  [PASS ] G14 [opponent] at 0:57
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [PASS ] G15 'certificate' planted at 0:09
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [PASS ] G15b close shares 4 content stem(s) with the P1 claim (need 2); claim stems: ['bubble', 'carry', 'last', 'paid', 'paper', 'safety', 'sold', 'steel']
          Ring MECHANISM: the claim planted with the token in P1 recurs in the close (47 s2 G-g)
  [PASS ] G16 1 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 2 marks in P1 (1.7/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G19 closed by [loop] at 1:29
          The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)
  [PASS ] G20 longest gap 28s
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2)
  [PASS ] G21 3 [loop] in P2
          L2 loops: 3-4 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [PASS ] G22 7 [new] in P2
          PLATFORM density: 5-7 new-info beats at this runtime (P2 geometry)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G24 [head-fake] at 1:33
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [PASS ] G25 A3 at 1:06
          PLATFORM rehook A3 at ~10% of runtime = 1:23 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G26 [foreshadow] at 1:14
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [PASS ] G27 'certificate' 1x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [PASS ] G28 [loop-close] at 2:28
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [PASS ] G29 [dip] at 2:35
          PLATFORM breathing dip IMMEDIATELY after the macro close - 2-3 beats of room tone (P2)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G32 tricolon 0, anaphora P1 0 / P2 1
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 0 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G34 clean
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [PASS ] G35 clean
          U6 / E20: a delivered proof is never hedged in the next sentence
  [PASS ] G36 longest stretch without a cycle beat: 55s from 12:22
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-13:58 (E23: whole runtime)
  [PASS ] G37 [archetype] at 0:21
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [PASS ] G38 [desire] at 0:51
          Truby Desire named: the goal the video pursues (38 B5)
  [PASS ] G39 [map] at 0:55
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [PASS ] G40 [catalyst] at 1:29
          Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)
  [PASS ] G41 [debate] at 2:19
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [PASS ] G42 [signpost] at 2:38
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [PASS ] G44 all 4 unit windows rehook out
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [PASS ] G45 title-word proxy: ['ai', 'bubble', 'real'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] G46 runtime 13:58 (measured) clears the 8:00 floor
          E74: long form is never under 8 minutes (the operator, 2026-09-13: 'yes, longform should never be under 8 minutes'; 2026-08-29: 'i dont think we make vdieos shorter than 8 minutes') - a cut under 8:00 is extended with substance or run as a short (under 3:00, G2), never shipped as a long form in between
  [PASS ] G47 no self-referential runtime claim
          A script's promises about itself: a self-referential runtime ('the next eight minutes', 'this ten-minute video') agrees with the clock within max(60 s, 15%) - FAIL on a measured take, WARN on the estimate; a deadline ('in the next N minutes') breaks only past the end (C03-R011, ledger e319a9d02fe4: 'The script promised eight minutes and ran twelve.')
  [PASS ] G47b 1 counted promise(s) agree with what the script names
          A script's promises about itself: a counted promise ('the five', 'three questions') agrees with the items the script names - the nearest named list, or the ordinals it walks - heuristic, so WARN (C03-R011, ledger e319a9d02fe4: 'A viewer counts four and then hears five.')
  [JUDGE] J01 read the [opponent] line at 0:57
          McKee antagonism: the opponent is a mechanism, not a villain
  [JUDGE] J02 read the line at 1:33
          P2: the head-fake is offered STRAIGHT, no wink; demolition reserved for the pivot
  [JUDGE] J03 'The AI bubble is real.'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'The AI bubble is real.' -> 'Just not in the steel.'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J09 read the line at 0:21
          McKee archetype, not stereotype: a universal experience in a specific setting (doc 32 s4)
  [JUDGE] J10 read the line at 0:55
          38 B5: the map is a journey tease, never a table of contents
  [JUDGE] J11 read the line at 2:19
          McKee: the plan fails as a GAP (an action whose result violates expectation), never as a lecture
  [JUDGE] J12 open content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/thumbnail-FINAL-steelpaper.png; sentence 1: 'The AI bubble is real.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it

RESULT: 0 FAIL / 3 WARN / 47 PASS / 12 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-H-SCREENS.md: X1=76 deixis=29 junctions=22 anchors=50 declared=52
```

VERDICT: PASS
