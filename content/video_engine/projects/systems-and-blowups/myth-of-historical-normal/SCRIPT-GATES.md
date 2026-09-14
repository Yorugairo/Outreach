# SCRIPT GATES - SCRIPT-VO.txt

script: SCRIPT-VO.txt
generated: 2026-09-11T23:20:27+00:00
script_hash: 87bddb106f5c421db5327d96f39008b371616bd5579d7104a87c2f21c3581770
timing_source: estimated

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/0, timing=estimated |
           opening gate: exit 0, 0/0/43/12 | screens: SCRIPT-SCREENS.md, 94 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
stats: {'sentence_mean': 12.3, 'sentence_count': 126, 'word_count': 1546, 'rehook_positions_pct': [67]}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-VO.txt ===
             chars: 9669
         runtime_s: 568.2
           runtime: 9m 28s
         sentences: 126
     sentence_mean: 12.3
      break_ration: 0.31
  sentence_mean_carrying: 12.7
  short_figure_share: 4.8%
    sentence_stdev: 4.8
     over_20_share: 7.9%
       hook_spread: 2%
   hook_properties: present-tense=y, viewer-facing=y
         paradox_s: 4.0
       first_you_s: 0.0
         cta_count: 1
           rehooks: ['6.3m']
         phase_map: {'P1 OPEN': '0.0-1.2m', 'P2 ENGINE': '1.2-2.4m', 'P3 GAP': '1.6-4.3m', 'P4 PIVOT': '4.3-5.2m', 'P5 REFLECTION': '5.2-8.2m', 'P6 CLOSE': '8.0-9.5m'}
  p3_units_expected: 1
         a3_anchor: 0:56
         pivot_pct: None
     timing_source: estimated (no take on disk)

  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\myth-of-historical-normal\SCRIPT-GATES.md

RESULT: 0 FAIL, 0 WARN
```

## gate_opening_structure.py
exit 0

```
=== OPENING STRUCTURE GATE: SCRIPT-VO.txt ===
           runtime: 9:24
            timing: estimated (kit rate, 8% band)
          geometry: P1 0:00-1:02 (beat 5 from 0:41), P2 -2:22 (phase guides)
     density_bands: loops (2, 3), new-info (4, 6)
         a3_anchor: 0:56
             cycle: checked 0:00-9:24; longest gap 52s from 7:02
      unit_windows: ['P3 unit 1 1:35-4:13', 'P5 unit 2 5:10-8:10']
      counterparty: Federal
              ring: None
         packaging: title=None thumb=None thumb_file=None
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'ring': ['0:02', '1:40', '5:41', '7:54'], 'archetype': ['0:07'], 'stakes': ['0:17'], 'payoff': ['0:22', '6:05'], 'reflect': ['0:35', '2:03', '5:57'], 'tricolon': ['0:40', '8:46'], 'promise': ['0:44'], 'desire': ['0:51'], 'opponent': ['0:54'], 'map': ['0:59'], 'rehook': ['1:07', '3:10', '4:16', '6:13'], 'catalyst': ['1:12'], 'new': ['1:18', '1:31', '1:48', '2:08', '2:11', '2:59', '3:23', '3:33', '4:31', '5:17', '6:32', '6:47'], 'foreshadow': ['1:24', '5:07'], 'head-fake': ['1:29'], 'debate': ['1:45'], 'loop': ['1:54', '2:29', '7:02'], 'loop-close': ['2:31'], 'dip': ['2:34'], 'signpost': ['2:36', '4:55'], 'anaphora': ['2:40', '4:52']}

  [PASS ] G01 first sentence 2.49s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G03 paid at 3.93s, settle at 5.66s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:00
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:17
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:22
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G09 promise at 0:44
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G10 placed
          Humes pre-key immediately before the promise (P1 pause marks)
  [PASS ] G11 'One test — three mechanical questions — that proves whether your portf'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G12 1 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [PASS ] G13 A2 at 1:07
          PLATFORM rehook A2 ~1:00, template family (38 B5 / P1 QC)
  [PASS ] G14 [opponent] at 0:54
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [PASS ] G15 [ring] at 0:02
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [PASS ] G16 1 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 2 marks in P1 (1.9/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G19 closed by [loop] at 1:54
          The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)
  [PASS ] G20 longest gap 19s
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2)
  [PASS ] G21 2 [loop] in P2
          L2 loops: 2-3 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [PASS ] G22 5 [new] in P2
          PLATFORM density: 4-6 new-info beats at this runtime (P2 geometry)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G24 [head-fake] at 1:29
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [PASS ] G25 A3 at 1:07
          PLATFORM rehook A3 at ~10% of runtime = 0:56 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G26 [foreshadow] at 1:24
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [PASS ] G27 [ring] 1x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [PASS ] G28 [loop-close] at 2:31
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [PASS ] G29 [dip] at 2:34
          PLATFORM breathing dip IMMEDIATELY after the macro close - 2-3 beats of room tone (P2)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G31 1 dabs, 2 loops
          Glass alternation, P2 70/30: dabs marked, never consecutive (P2)
  [PASS ] G32 tricolon 0, anaphora P1 0 / P2 0
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 0 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G34 clean
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [PASS ] G35 clean
          U6 / E20: a delivered proof is never hedged in the next sentence
  [PASS ] G36 longest stretch without a cycle beat: 52s from 7:02
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-9:24 (E23: whole runtime)
  [PASS ] G37 [archetype] at 0:07
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [PASS ] G38 [desire] at 0:51
          Truby Desire named: the goal the video pursues (38 B5)
  [PASS ] G39 [map] at 0:59
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [PASS ] G40 [catalyst] at 1:12
          Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)
  [PASS ] G41 [debate] at 1:45
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [PASS ] G42 [signpost] at 2:36
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [PASS ] G43 7/8 declared beats open on a gap/consequence connector
          McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)
  [PASS ] G44 all 2 unit windows rehook out
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [INFO ] G02 edit-clock property - checked with --timeline
          Humes pre-opener, bent visual: plate breathes 0.5-0.8s before the first word
  [INFO ] G45 no --title given, G45 not run
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [JUDGE] J01 read the [opponent] line at 0:54
          McKee antagonism: the opponent is a mechanism, not a villain
  [JUDGE] J02 read the line at 1:29
          P2: the head-fake is offered STRAIGHT, no wink; demolition reserved for the pivot
  [JUDGE] J03 'Your core holding breaks at five percent.'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'Your core holding breaks at five percent.' -> 'Five point five percent.'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J09 read the line at 0:07
          McKee archetype, not stereotype: a universal experience in a specific setting (doc 32 s4)
  [JUDGE] J10 read the line at 0:59
          38 B5: the map is a journey tease, never a table of contents
  [JUDGE] J11 read the line at 1:45
          McKee: the plan fails as a GAP (an action whose result violates expectation), never as a lecture
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'Your core holding breaks at five percent.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it

RESULT: 0 FAIL / 0 WARN / 43 PASS / 12 JUDGE (read these) / 2 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-SCREENS.md: X1=35 deixis=14 junctions=5 anchors=40 declared=47
```

VERDICT: PASS
