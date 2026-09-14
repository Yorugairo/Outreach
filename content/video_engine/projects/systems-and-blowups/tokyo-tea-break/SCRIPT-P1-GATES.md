# SCRIPT GATES - SCRIPT-P1-VO.txt

script: SCRIPT-P1-VO.txt
generated: 2026-09-05T04:32:14+00:00
script_hash: 5ce7e0ae6002581f99c9efb48c31ce6adb398c808412aa8a5fea42b0eb88fc43
timing_source: estimated

TOOLS      lint: exit 0, 0 fails | audit: exit 1, 2/5, timing=estimated |
           opening gate: exit 1, 23/1/19/7 | screens: SCRIPT-P1-SCREENS.md, 6 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 14.9, 'sentence_count': 14, 'word_count': 209, 'rehook_positions_pct': []}
RESULT: clean
```

## audit_script_doctrine.py
exit 1

```
=== SCRIPT-P1-VO.txt ===
             chars: 1220
         runtime_s: 75.0
           runtime: 1m 15s
         sentences: 14
     sentence_mean: 14.9
      break_ration: 1.64
  sentence_mean_carrying: 15.8
  short_figure_share: 7.1%
    sentence_stdev: 7.9
     over_20_share: 28.6%
       hook_spread: 4%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 7.2
       first_you_s: 5.8
         cta_count: 0
           rehooks: []
         phase_map: {'P1 OPEN': '0.0-0.2m', 'P2 ENGINE': '0.2-1.4m', 'P3 GAP': '0.2-0.6m', 'P4 PIVOT': '0.6-0.7m', 'P5 REFLECTION': '0.7-1.1m', 'P6 CLOSE': '-0.2-1.3m'}
  p3_units_expected: 1
         a3_anchor: 0:07
         pivot_pct: None
     timing_source: estimated (no take on disk)

  [FAIL] doc 37 sec 4: narration carries digit numerals (badges take digits, narration takes words): ['1.1', '5.5%', '5%']
  [FAIL] doc 35 rule 2: no falsifiable tell — an answer video must name one variable, one threshold, where we sit, and what flips us
  [WARN] doc 32 sec 1 / doc 33: sentence mean 15.8 words (excluding sub-5-word figures) is outside the 10-15 band for speech; raw mean 14.9
  [WARN] doc 32 sec 1: 29% of sentences run past 20 words (max 12%) — the range where listener comprehension drops
  [WARN] MAP sec 1: P1 computes to 10s; the open is pinned 60-90s at every runtime
  [WARN] MAP sec 2: no rehook construction within 45s of anchor(s) A1, A2, A3 (A1 ~0:30, A2 ~1:00, A3 ~0:07 at 1:15 = 10% of runtime) — found at none
  [WARN] doc 35 rule 2: the tell does not state what being wrong looks like
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\tokyo-tea-break\SCRIPT-P1-GATES.md

RESULT: 2 FAIL, 5 WARN
```

## gate_opening_structure.py
exit 1

```
=== OPENING STRUCTURE GATE: SCRIPT-P1-VO.txt ===
           runtime: 1:10
            timing: estimated (kit rate, 8% band)
          geometry: P1 0:00-0:35 (beat 5 from 0:23), P2 -1:05 (phase guides)
     density_bands: loops (2, 3), new-info (4, 6)
         a3_anchor: 0:07
             cycle: checked 0:00-1:10; longest gap 13s from 0:47
      unit_windows: ['P3 unit 1 0:12-0:31', 'P5 unit 2 0:38-1:01']
      counterparty: Japan
              ring: tea break
         packaging: title='Tokyo Tea Break' thumb=None thumb_file=None
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'archetype': ['0:07'], 'stakes': ['0:18'], 'payoff': ['0:21'], 'tricolon': ['0:33'], 'promise': ['0:38'], 'desire': ['0:38'], 'rehook': ['0:47'], 'ring': ['1:00'], 'opponent': ['1:04']}

  [FAIL ] G01 first sentence 5.72s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [FAIL ] G03 no [post-key] settle by the 8s boundary
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [FAIL ] G10 missing
          Humes pre-key immediately before the promise (P1 pause marks)
  [FAIL ] G13 no rehook construction in 0:55-0:35
          PLATFORM rehook A2 ~1:00, template family (38 B5 / P1 QC)
  [FAIL ] G14 no [opponent] declared in P1
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [FAIL ] G15 'tea break' never mentioned in P1
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [FAIL ] G15b no P1 sentence carries the token, so there is no claim to return to
          Ring MECHANISM: the claim planted with the token in P1 recurs in the close (47 s2 G-g)
  [FAIL ] G16 0 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [FAIL ] G18 2 marks in P1 (3.4/min)
          Humes pauses rationed: ~three per minute maximum (P1)
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
  [FAIL ] G28 no [loop-close] declared
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
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
  [FAIL ] G44 no rehook in unit 1 0:12-0:31
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [FAIL ] G45 title-word proxy: none of ['tokyo', 'tea', 'break'] in the first two sentences - the first sentence must answer the thumbnail
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [WARN ] G29 cannot place - macro close not declared
          PLATFORM breathing dip after the macro close (P2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:05
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:18
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:21
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G09 promise at 0:38
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G11 'In the next eight minutes, we’ll show you where this risk is hidden in'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G12 1 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G25 A3 at 0:47
          PLATFORM rehook A3 at ~10% of runtime = 0:07 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G27 'tea break' 1x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G31 0 dabs, 0 loops
          Glass alternation, P2 70/30: dabs marked, never consecutive (P2)
  [PASS ] G32 tricolon 1, anaphora P1 0 / P2 0
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 1 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G34 clean
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [PASS ] G35 clean
          U6 / E20: a delivered proof is never hedged in the next sentence
  [PASS ] G36 longest stretch without a cycle beat: 13s from 0:47
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-1:10 (E23: whole runtime)
  [INFO ] G02 edit-clock property - checked with --timeline
          Humes pre-opener, bent visual: plate breathes 0.5-0.8s before the first word
  [JUDGE] J03 'US bond yields crossed critical levels, but the Federal Reserve didn't move an i'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'US bond yields crossed critical levels, but the Fe' -> 'Your costs jumped anyway.'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'US bond yields crossed critical levels, but the Federal Reserve didn't move an i'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it

RESULT: 23 FAIL / 1 WARN / 19 PASS / 7 JUDGE (read these) / 1 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-P1-SCREENS.md: X1=1 deixis=0 junctions=0 anchors=5 declared=9
```

VERDICT: FAIL (2 failing tools)
