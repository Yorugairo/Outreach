# SCRIPT GATES - SCRIPT-90S-VO.txt

script: SCRIPT-90S-VO.txt
generated: 2026-09-04T02:39:41+00:00
script_hash: dd06a62ba022ba367ca6a5c7a67f0880021961cc6f9bc3d6d07119d7a0f5ea2d
timing_source: estimated

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/1, timing=estimated |
           opening gate: exit 1, 17/1/23/7 | screens: SCRIPT-90S-SCREENS.md, 16 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
stats: {'sentence_mean': 9.0, 'sentence_count': 31, 'word_count': 278, 'rehook_positions_pct': [14, 34]}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-90S-VO.txt ===
             chars: 1546
         runtime_s: 96.3
           runtime: 1m 36s
         sentences: 31
     sentence_mean: 9.0
      break_ration: 0.65
  sentence_mean_carrying: 10.2
  short_figure_share: 16.1%
    sentence_stdev: 5.4
     over_20_share: 3.2%
       hook_spread: 8%
   hook_properties: present-tense=y, viewer-facing=y
         paradox_s: 6.4
       first_you_s: 0.0
         cta_count: 0
           rehooks: ['0.2m', '0.5m']
         phase_map: {'P1 OPEN': '0.0-0.2m', 'P2 ENGINE': '0.2-1.5m', 'P3 GAP': '0.3-0.7m', 'P4 PIVOT': '0.7-0.9m', 'P5 REFLECTION': '0.9-1.4m', 'P6 CLOSE': '0.1-1.6m'}
  p3_units_expected: 1
         a3_anchor: 0:09
         pivot_pct: None
     timing_source: estimated (no take on disk)

  [WARN] MAP sec 1: P1 computes to 13s; the open is pinned 60-90s at every runtime
  [INFO] estimator: the two rate estimates disagree by 8% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\tokyo-tea-break\SCRIPT-90S-GATES.md

RESULT: 0 FAIL, 1 WARN
```

## gate_opening_structure.py
exit 1

```
=== OPENING STRUCTURE GATE: SCRIPT-90S-VO.txt ===
           runtime: 1:35
            timing: estimated (kit rate, 8% band)
          geometry: P1 0:00-0:35 (beat 5 from 0:23), P2 -1:05 (phase guides)
     density_bands: loops (2, 3), new-info (4, 6)
         a3_anchor: 0:09
             cycle: checked 0:00-1:35; longest gap 31s from 0:56
      unit_windows: ['P3 unit 1 0:16-0:42', 'P5 unit 2 0:52-1:22']
      counterparty: Tokyo
              ring: tea break
         packaging: title=None thumb=None thumb_file=None
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'archetype': ['0:06'], 'stakes': ['0:10'], 'rehook': ['0:12', '0:56'], 'payoff': ['0:16'], 'promise': ['0:23'], 'head-fake': ['0:31'], 'debate': ['0:39'], 'loop-close': ['0:44'], 'ring': ['0:48', '1:29'], 'opponent': ['0:51'], 'tricolon': ['1:27']}

  [FAIL ] G10 missing
          Humes pre-key immediately before the promise (P1 pause marks)
  [FAIL ] G12 0 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [FAIL ] G14 no [opponent] declared in P1
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [FAIL ] G15 'tea break' never mentioned in P1
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [FAIL ] G16 0 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [FAIL ] G20 no [new] beats declared in P2
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2)
  [FAIL ] G21 0 [loop] in P2
          L2 loops: 2-3 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [FAIL ] G22 0 [new] in P2
          PLATFORM density: 4-6 new-info beats at this runtime (P2 geometry)
  [FAIL ] G24 no [head-fake] declared in P2
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [FAIL ] G26 no [foreshadow] near 10%
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [FAIL ] G29 no dip within 15s of the macro close at 0:44
          PLATFORM breathing dip IMMEDIATELY after the macro close - 2-3 beats of room tone (P2)
  [FAIL ] G37 no [archetype] declared in 0:08-0:30
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [FAIL ] G38 no [desire] declared in 0:23-0:35
          Truby Desire named: the goal the video pursues (38 B5)
  [FAIL ] G39 no [map] declared in beat 5
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [FAIL ] G40 no [catalyst] declared in the phase's first 60s
          Snyder Catalyst / McKee inciting incident: the fact that makes the question urgent lands as a story beat in P2's first ~60s (P2)
  [FAIL ] G41 no [debate] declared after the head-fake in mid-late P2
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [FAIL ] G42 no [signpost] declared at the end of P2
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [WARN ] G09 promise at 0:23 - before the mini-payoff window opens
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G01 first sentence 1.47s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G03 paid at 6.38s, settle at 6.38s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:00
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:10
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:16
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G11 'By the end of this minute you'll know the number that says whether the'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G13 A2 at 0:56
          PLATFORM rehook A2 ~1:00, template family (38 B5 / P1 QC)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 1 marks in P1 (1.7/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G25 A3 at 0:12
          PLATFORM rehook A3 at ~10% of runtime = 0:09 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G27 'tea break' 1x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [PASS ] G28 [loop-close] at 0:44
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G31 0 dabs, 0 loops
          Glass alternation, P2 70/30: dabs marked, never consecutive (P2)
  [PASS ] G32 tricolon 0, anaphora P1 0 / P2 0
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 0 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G34 clean
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [PASS ] G35 clean
          U6 / E20: a delivered proof is never hedged in the next sentence
  [PASS ] G36 longest stretch without a cycle beat: 31s from 0:56
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-1:35 (E23: whole runtime)
  [PASS ] G44 all 2 unit windows rehook out
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [INFO ] G02 edit-clock property - checked with --timeline
          Humes pre-opener, bent visual: plate breathes 0.5-0.8s before the first word
  [INFO ] G45 no --title given, G45 not run
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [JUDGE] J03 'Your costs jumped anyway.'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'Your costs jumped anyway.' -> 'Bond yields crossed critical levels this month, an'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'Your costs jumped anyway.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it

RESULT: 17 FAIL / 1 WARN / 23 PASS / 7 JUDGE (read these) / 2 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-90S-SCREENS.md: X1=5 deixis=3 junctions=1 anchors=7 declared=13
```

VERDICT: FAIL (1 failing tools)
