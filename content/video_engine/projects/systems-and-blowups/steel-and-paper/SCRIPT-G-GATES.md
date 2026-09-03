# SCRIPT GATES - SCRIPT-G-VO.txt

script: SCRIPT-G-VO.txt
generated: 2026-09-03T11:32:27+00:00
script_hash: 4d2876620021c3d94387d761d442548d95f867afeb7be8db00f3ed3385dcf5f8
timing_source: measured

TOOLS      lint: exit 0, 0 fails | audit: exit 1, 1/0, timing=measured |
           opening gate: exit 1, 22/2/21/8 | screens: SCRIPT-G-SCREENS.md, 186 items

VIEWER     SCRIPT-G-VIEWER.md
  [FAIL ] V01 25/37 declared beats perceived (68%); unperceived: [payoff] w2, [reflect] w4, [opponent] w5, [rehook] w6, [concede] w12, [loop] w16, [loop-close] w17, [anaphora] w25 +4 more
  [WARN ] V04 15 window(s) with something unfollowable: 0:15-0:30 What exactly AI is being compared to in 1845; 2:45-3:00 The new yardstick is not defined yet.; 3:15-3:30 The meaning of risk charts failing by pointing; 4:00-4:15 What the four months refers to.
  [PASS ] V02 no run of 2+ windows without a concrete new thing
  [PASS ] V03 open loop live in 48/54 windows (89%)
  [INFO ] V05 gain per window: median 3, 0 dead of 54 reported

## lint_script_pattern.py
exit 0

```
stats: {'sentence_mean': 10.1, 'sentence_count': 240, 'word_count': 2417, 'rehook_positions_pct': [26, 34]}
RESULT: clean
```

## audit_script_doctrine.py
exit 1

```
=== SCRIPT-G-VO.txt ===
             chars: 13883
         runtime_s: 851.8
           runtime: 14m 11s
         sentences: 240
     sentence_mean: 10.1
      break_ration: 3.1
  sentence_mean_carrying: 11.4
  short_figure_share: 16.2%
    sentence_stdev: 5.2
     over_20_share: 3.3%
       hook_spread: 10%
   hook_properties: present-tense=y, viewer-facing=y
         paradox_s: 3.6
       first_you_s: 1.0
         cta_count: 1
           rehooks: ['3.7m', '4.4m', '4.8m', '7.9m']
         phase_map: {'P1 OPEN': '0.0-1.5m', 'P2 ENGINE': '1.5-3.0m', 'P3 GAP': '2.4-6.4m', 'P4 PIVOT': '6.4-7.8m', 'P5 REFLECTION': '7.8-12.4m', 'P6 CLOSE': '12.7-14.2m'}
  p3_units_expected: 3
         a3_anchor: 1:25
         pivot_pct: None
     timing_source: measured (2883 words on disk)
   hook_measured_s: 2.42
  paradox_measured_s: 3.63

  [FAIL] doc 37 sec 1: break ration 3.10/1k exceeds 3.0 — causes audible speed-ups
  [INFO] doc 37 sec 8: 13,883 chars exceeds the mv2 10,000 cap — chained take required, split at a phase boundary
  [INFO] estimator: the two rate estimates disagree by 10% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\steel-and-paper\SCRIPT-G-GATES.md

RESULT: 1 FAIL, 0 WARN
```

## gate_opening_structure.py
exit 1

```
=== OPENING STRUCTURE GATE: SCRIPT-G-VO.txt ===
           runtime: 13:25
            timing: measured (take)
          geometry: P1 0:00-1:10 (beat 5 from 0:47), P2 -2:45 (phase guides)
     density_bands: loops (3, 4), new-info (5, 7)
         a3_anchor: 1:20
             cycle: checked 0:00-13:25; longest gap 130s from 9:26
      unit_windows: ['P3 unit 1 2:16-4:09', 'P3 unit 2 4:09-6:02', 'P5 unit 3 7:23-9:32', 'P5 unit 4 9:32-11:40']
      counterparty: Bravos
              ring: spike
         packaging: title='The AI Bubble Is Real. What Survives Is Steel.' thumb=None thumb_file=content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/thumbnail-FINAL-steelpaper.png
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'ring': ['0:02', '7:15', '11:36'], 'archetype': ['0:09'], 'stakes': ['0:28'], 'payoff': ['0:30'], 'reflect': ['1:07'], 'tricolon': ['1:10'], 'promise': ['1:15'], 'desire': ['1:20'], 'opponent': ['1:23'], 'rehook': ['1:32'], 'map': ['1:33'], 'catalyst': ['1:43'], 'foreshadow': ['1:45', '6:44'], 'new': ['1:53', '1:59', '2:24', '3:03', '3:48', '4:52', '5:36', '5:54', '9:26'], 'concede': ['3:16'], 'turn': ['3:24'], 'head-fake': ['3:31'], 'debate': ['3:41'], 'loop': ['4:15'], 'loop-close': ['4:22'], 'dip': ['4:30'], 'anaphora': ['4:39', '6:23', '8:51', '12:53'], 'signpost': ['6:31']}

  [FAIL ] G02 first word at 0.00s in the edit clock
          Humes pre-opener, bent visual: the plate breathes 0.5-0.8s before the first word (38 B1 / doc 32 s7)
  [FAIL ] G09 promise at 1:15 - AFTER 0:45 (E24, decided 2026-09-03; Steel and Paper as recorded: 1:20)
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [FAIL ] G10 missing
          Humes pre-key immediately before the promise (P1 pause marks)
  [FAIL ] G12 0 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [FAIL ] G13 no rehook construction in 0:55-1:10
          PLATFORM rehook A2 ~1:00, template family (38 B5 / P1 QC)
  [FAIL ] G14 no [opponent] declared in P1
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [FAIL ] G19 no [loop] within 60s of the catalyst at 1:43
          The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)
  [FAIL ] G20 longest gap 44s
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2)
  [FAIL ] G21 0 [loop] in P2
          L2 loops: 3-4 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [FAIL ] G22 3 [new] in P2
          PLATFORM density: 5-7 new-info beats at this runtime (P2 geometry)
  [FAIL ] G24 no [head-fake] declared in P2
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [FAIL ] G27 'spike' 0x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [FAIL ] G28 no [loop-close] declared
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [FAIL ] G34 5 sentences, 3:10-3:24 (13s): 'So Bravos' tripwire for this cycle: the Fed back above five ...'
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [FAIL ] G35 proof at 2:44 hedged at 2:47: 'The yardstick is a new instrument for this channel — no threshold on i'
          U6 / E20: a delivered proof is never hedged in the next sentence
  [FAIL ] G36 longest stretch without a cycle beat: 130s from 9:26
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-13:25 (E23: whole runtime)
  [FAIL ] G38 no [desire] declared in 0:47-1:10
          Truby Desire named: the goal the video pursues (38 B5)
  [FAIL ] G39 no [map] declared in beat 5
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [FAIL ] G41 no [debate] declared after the head-fake in mid-late P2
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [FAIL ] G42 no [signpost] declared at the end of P2
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [FAIL ] G44 no rehook in unit 4 9:32-11:40
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [FAIL ] G45 title-word proxy: none of ['ai', 'bubble', 'real', 'surviv', 'steel'] in the first two sentences - the first sentence must answer the thumbnail
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [WARN ] G29 cannot place - macro close not declared
          PLATFORM breathing dip after the macro close (P2)
  [WARN ] G43 1/4 declared beats open on a gap/consequence connector
          McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)
  [PASS ] G01 first sentence 2.42s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G03 paid at 3.63s, settle at 5.57s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:00
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:28
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:30
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G11 'One test — three questions — that sorts every holding you own into ste'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G15 'spike' planted at 0:02
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [PASS ] G16 1 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 1 marks in P1 (0.9/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G25 A3 at 1:32
          PLATFORM rehook A3 at ~10% of runtime = 1:20 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G26 [foreshadow] at 1:45
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G31 0 dabs, 0 loops
          Glass alternation, P2 70/30: dabs marked, never consecutive (P2)
  [PASS ] G32 tricolon 1, anaphora P1 0 / P2 0
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 1 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G37 [archetype] at 0:09
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [PASS ] G40 [catalyst] at 1:43
          Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)
  [JUDGE] J03 'The safest thing you own looks like this.'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'The safest thing you own looks like this.' -> 'An iron spike.'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J09 read the line at 0:09
          McKee archetype, not stereotype: a universal experience in a specific setting (doc 32 s4)
  [JUDGE] J12 open content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/thumbnail-FINAL-steelpaper.png; sentence 1: 'The safest thing you own looks like this.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it

RESULT: 22 FAIL / 2 WARN / 21 PASS / 8 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-G-SCREENS.md: X1=86 deixis=32 junctions=24 anchors=44 declared=37
```

VERDICT: FAIL (2 failing tools, 1 viewer)
