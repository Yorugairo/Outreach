# SCRIPT GATES - SCRIPT-90S-VO.claude.txt

script: SCRIPT-90S-VO.claude.txt
generated: 2026-09-05T05:25:41+00:00
script_hash: d26bd48daf05ed3aeb65f226c5fed2001e205b20a715819e7a21383afc50d728
timing_source: estimated

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/1, timing=estimated |
           opening gate: exit 1, 3/2/40/10 | screens: SCRIPT-90S.claude-SCREENS.md, 7 items

VIEWER     SCRIPT-90S.claude-VIEWER.md  (advisory: --no-viewer-gate - these rows do not change the VERDICT)
  [INFO ] V01 21/24 declared beats perceived (88%); unperceived: [stakes] w0, [promise] w2, [rehook] w2
  [INFO ] V04 1 window(s) with something unfollowable: 0:00-0:15 What “Tokyo took a tea break” means
  [INFO ] V02 no run of 2+ windows without a concrete new thing
  [INFO ] V03 open loop live in 6/7 windows (86%)
  [INFO ] V05 gain per window: median 4, 0 dead of 7 reported

## lint_script_pattern.py
exit 0

```
stats: {'sentence_mean': 10.4, 'sentence_count': 27, 'word_count': 281, 'rehook_positions_pct': [17, 64]}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-90S-VO.claude.txt ===
             chars: 1539
         runtime_s: 96.6
           runtime: 1m 36s
         sentences: 27
     sentence_mean: 10.4
      break_ration: 1.95
  sentence_mean_carrying: 11.4
  short_figure_share: 11.1%
    sentence_stdev: 5.7
     over_20_share: 3.7%
       hook_spread: 20%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 4.3
       first_you_s: 6.0
         cta_count: 0
           rehooks: ['0.3m', '1.0m']
         phase_map: {'P1 OPEN': '0.0-0.2m', 'P2 ENGINE': '0.2-1.5m', 'P3 GAP': '0.3-0.7m', 'P4 PIVOT': '0.7-0.9m', 'P5 REFLECTION': '0.9-1.4m', 'P6 CLOSE': '0.1-1.6m'}
  p3_units_expected: 1
         a3_anchor: 0:09
         pivot_pct: None
     timing_source: estimated (no take on disk)

  [WARN] MAP sec 1: P1 computes to 13s; the open is pinned 60-90s at every runtime
  [INFO] estimator: the two rate estimates disagree by 20% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\tokyo-tea-break\SCRIPT-90S.claude-GATES.md

RESULT: 0 FAIL, 1 WARN
```

## gate_opening_structure.py
exit 1

```
=== OPENING STRUCTURE GATE: SCRIPT-90S-VO.claude.txt ===
           runtime: 1:35
            timing: estimated (kit rate, 8% band)
          geometry: P1 0:00-0:35 (beat 5 from 0:23), P2 -1:05 (phase guides)
     density_bands: loops (2, 3), new-info (4, 6)
         a3_anchor: 0:09
             cycle: checked 0:00-1:35; longest gap 18s from 1:15
      unit_windows: ['P3 unit 1 0:16-0:43', 'P5 unit 2 0:52-1:23']
      counterparty: Japan
              ring: tab
         packaging: title='Tokyo Tea Break' thumb=None thumb_file=None
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'stakes': ['0:04'], 'archetype': ['0:07'], 'tricolon': ['0:07'], 'rehook': ['0:15', '0:39', '0:59'], 'payoff': ['0:19'], 'new': ['0:19', '0:42', '0:48', '0:53'], 'reflect': ['0:26'], 'opponent': ['0:31'], 'desire': ['0:35'], 'map': ['0:35'], 'promise': ['0:39'], 'catalyst': ['0:42'], 'loop': ['0:48', '0:53'], 'foreshadow': ['0:48'], 'loop-close': ['0:59'], 'dip': ['1:15'], 'signpost': ['1:15'], 'ring': ['1:33']}

  [FAIL ] G22 3 [new] in P2
          PLATFORM density: 4-6 new-info beats at this runtime (P2 geometry)
  [FAIL ] G24 no [head-fake] declared in P2
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [FAIL ] G41 no [debate] declared after the head-fake in mid-late P2
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [WARN ] G31 0 dabs for 2 loops
          Glass alternation, P2 70/30: two loops with no reflection = listing (P2)
  [WARN ] G43 1/3 declared beats open on a gap/consequence connector
          McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)
  [PASS ] G01 first sentence 1.58s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G03 paid at 4.28s, settle at 4.28s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:04
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:04
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:19
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G09 promise at 0:39
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G10 placed
          Humes pre-key immediately before the promise (P1 pause marks)
  [PASS ] G11 'By the end you'll read both numbers yourself.'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G12 1 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [PASS ] G13 A2 at 0:59
          PLATFORM rehook A2 ~1:00, template family (38 B5 / P1 QC)
  [PASS ] G14 [opponent] at 0:31
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [PASS ] G15 'tab' planted at 0:01
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [PASS ] G15b close shares 2 content stem(s) with the P1 claim (need 2); claim stems: ['america', 'bar', 'left', 'unfund']
          Ring MECHANISM: the claim planted with the token in P1 recurs in the close (47 s2 G-g)
  [PASS ] G16 1 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 1 marks in P1 (1.7/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G19 closed by [loop] at 0:48
          The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)
  [PASS ] G20 longest gap 7s
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2)
  [PASS ] G21 2 [loop] in P2
          L2 loops: 2-3 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G25 A3 at 0:15
          PLATFORM rehook A3 at ~10% of runtime = 0:09 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G26 [foreshadow] at 0:48
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [PASS ] G27 'tab' 1x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [PASS ] G28 [loop-close] at 0:59
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [PASS ] G29 [dip] at 1:15
          PLATFORM breathing dip IMMEDIATELY after the macro close - 2-3 beats of room tone (P2)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G32 tricolon 0, anaphora P1 0 / P2 0
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 2 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G34 clean
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [PASS ] G35 clean
          U6 / E20: a delivered proof is never hedged in the next sentence
  [PASS ] G36 longest stretch without a cycle beat: 18s from 1:15
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-1:35 (E23: whole runtime)
  [PASS ] G37 [archetype] at 0:07
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [PASS ] G38 [desire] at 0:35
          Truby Desire named: the goal the video pursues (38 B5)
  [PASS ] G39 [map] at 0:35
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [PASS ] G40 [catalyst] at 0:42
          Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)
  [PASS ] G42 [signpost] at 1:15
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [PASS ] G44 all 2 unit windows rehook out
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [PASS ] G45 title-word proxy: ['tokyo', 'tea', 'break'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [INFO ] G02 edit-clock property - checked with --timeline
          Humes pre-opener, bent visual: plate breathes 0.5-0.8s before the first word
  [JUDGE] J01 read the [opponent] line at 0:31
          McKee antagonism: the opponent is a mechanism, not a villain
  [JUDGE] J03 'Tokyo took a tea break.'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'Tokyo took a tea break.' -> 'And left America with an unfunded bar tab.'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J09 read the line at 0:07
          McKee archetype, not stereotype: a universal experience in a specific setting (doc 32 s4)
  [JUDGE] J10 read the line at 0:35
          38 B5: the map is a journey tease, never a table of contents
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'Tokyo took a tea break.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it

RESULT: 3 FAIL / 2 WARN / 40 PASS / 10 JUDGE (read these) / 1 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-90S.claude-SCREENS.md: X1=3 deixis=0 junctions=1 anchors=3 declared=24
```

VERDICT: FAIL (1 failing tools)
