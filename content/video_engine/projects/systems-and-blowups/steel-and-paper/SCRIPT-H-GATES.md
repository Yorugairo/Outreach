# SCRIPT GATES - SCRIPT-H-VO.txt

script: SCRIPT-H-VO.txt
generated: 2026-09-08T08:59:29+00:00
script_hash: b4c51d49e955d619046ed647ff8e735aa127940ec739a7c194ae329f03e026f9
timing_source: measured

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/0, timing=estimated |
           opening gate: exit 1, 2/2/42/12 | screens: SCRIPT-H-SCREENS.md, 175 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 11.0, 'sentence_count': 211, 'word_count': 2313, 'rehook_positions_pct': []}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-H-VO.txt ===
             chars: 13194
         runtime_s: 812.2
           runtime: 13m 32s
         sentences: 211
     sentence_mean: 11.0
      break_ration: 0.45
  sentence_mean_carrying: 12.2
  short_figure_share: 14.2%
    sentence_stdev: 6.1
     over_20_share: 7.1%
       hook_spread: 23%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 3.1
       first_you_s: 17.7
         cta_count: 1
           rehooks: ['2.2m', '7.0m']
         phase_map: {'P1 OPEN': '0.0-1.5m', 'P2 ENGINE': '1.5-2.9m', 'P3 GAP': '2.3-6.1m', 'P4 PIVOT': '6.1-7.4m', 'P5 REFLECTION': '7.4-11.8m', 'P6 CLOSE': '12.0-13.5m'}
  p3_units_expected: 2
         a3_anchor: 1:21
         pivot_pct: None
     timing_source: estimated (a take exists but is of DIFFERENT text — not used)

  [INFO] doc 37 sec 8: 13,194 chars exceeds the mv2 10,000 cap — chained take required, split at a phase boundary
  [INFO] estimator: the two rate estimates disagree by 23% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\steel-and-paper\SCRIPT-H-GATES.md

RESULT: 0 FAIL, 0 WARN
```

## gate_opening_structure.py
exit 1

```
=== OPENING STRUCTURE GATE: SCRIPT-H-VO.txt ===
           runtime: 7:26
            timing: measured (take)
          geometry: P1 0:00-0:55 (beat 5 from 0:37), P2 -2:01 (phase guides)
     density_bands: loops (2, 3), new-info (4, 6)
         a3_anchor: 0:44
             cycle: checked 0:00-7:26; longest gap 49s from 4:08
      unit_windows: ['P3 unit 1 1:15-3:20', 'P5 unit 2 4:05-6:28']
      counterparty: Bravos Research
              ring: certificate
         packaging: title='The AI Bubble Is Real. What Survives Is Steel.' thumb=None thumb_file=content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/thumbnail-FINAL-steelpaper.png
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'ring': ['0:00', '6:52', '7:23'], 'tricolon': ['0:03'], 'stakes': ['0:09'], 'archetype': ['0:21'], 'payoff': ['0:30'], 'reflect': ['0:37'], 'promise': ['0:39'], 'desire': ['0:46'], 'map': ['0:51'], 'opponent': ['0:53'], 'rehook': ['0:59', '3:52', '5:19'], 'catalyst': ['1:03'], 'foreshadow': ['1:05', '6:15'], 'new': ['1:15', '1:19', '1:38', '1:45', '1:50', '2:42', '3:21', '4:08', '4:57', '5:23', '7:23'], 'head-fake': ['1:22'], 'debate': ['1:34'], 'loop': ['1:56', '2:00'], 'loop-close': ['2:10'], 'dip': ['2:15'], 'signpost': ['2:17', '6:01'], 'anaphora': ['2:26', '5:53', '7:23', '7:23'], 'turn': ['3:03'], 'concede': ['3:37']}

  [FAIL ] G02 first word at 0.00s in the edit clock
          Humes pre-opener, bent visual: the plate breathes 0.5-0.8s before the first word (38 B1 / doc 32 s7)
  [FAIL ] G15b close shares 1 content stem(s) with the P1 claim (need 2); claim stems: ['actually', 'bubble', 'carry', 'last', 'paid', 'paper', 'safety', 'sold']
          Ring MECHANISM: the claim planted with the token in P1 recurs in the close (47 s2 G-g)
  [WARN ] G31 0 dabs for 2 loops
          Glass alternation, P2 70/30: two loops with no reflection = listing (P2)
  [WARN ] G43 1/8 declared beats open on a gap/consequence connector
          McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)
  [PASS ] G01 first sentence 2.21s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G03 paid at 3.50s, settle at 7.87s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:17
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:09
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:30
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G09 promise at 0:39
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G10 placed
          Humes pre-key immediately before the promise (P1 pause marks)
  [PASS ] G11 'One test, three questions, thirty seconds a holding, and it sorts ever'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G12 1 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [PASS ] G13 A2 at 0:59
          PLATFORM rehook A2 ~1:00, template family (38 B5 / P1 QC)
  [PASS ] G14 [opponent] at 0:53
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [PASS ] G15 'certificate' planted at 0:09
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [PASS ] G16 1 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 2 marks in P1 (2.2/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G19 closed by [loop] at 1:56
          The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)
  [PASS ] G20 longest gap 20s
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2)
  [PASS ] G21 2 [loop] in P2
          L2 loops: 2-3 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [PASS ] G22 5 [new] in P2
          PLATFORM density: 4-6 new-info beats at this runtime (P2 geometry)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G24 [head-fake] at 1:22
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [PASS ] G25 A3 at 0:59
          PLATFORM rehook A3 at ~10% of runtime = 0:44 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G26 [foreshadow] at 1:05
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [PASS ] G27 'certificate' 1x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [PASS ] G28 [loop-close] at 2:10
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [PASS ] G29 [dip] at 2:15
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
  [PASS ] G36 longest stretch without a cycle beat: 49s from 4:08
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-7:26 (E23: whole runtime)
  [PASS ] G37 [archetype] at 0:21
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [PASS ] G38 [desire] at 0:46
          Truby Desire named: the goal the video pursues (38 B5)
  [PASS ] G39 [map] at 0:51
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [PASS ] G40 [catalyst] at 1:03
          Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)
  [PASS ] G41 [debate] at 1:34
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [PASS ] G42 [signpost] at 2:17
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [PASS ] G44 all 2 unit windows rehook out
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [PASS ] G45 title-word proxy: ['ai', 'bubble', 'real'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [JUDGE] J01 read the [opponent] line at 0:53
          McKee antagonism: the opponent is a mechanism, not a villain
  [JUDGE] J02 read the line at 1:22
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
  [JUDGE] J10 read the line at 0:51
          38 B5: the map is a journey tease, never a table of contents
  [JUDGE] J11 read the line at 1:34
          McKee: the plan fails as a GAP (an action whose result violates expectation), never as a lecture
  [JUDGE] J12 open content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/thumbnail-FINAL-steelpaper.png; sentence 1: 'The AI bubble is real.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it

RESULT: 2 FAIL / 2 WARN / 42 PASS / 12 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-H-SCREENS.md: X1=76 deixis=29 junctions=20 anchors=50 declared=43
```

VERDICT: FAIL (1 failing tools)
