# SCRIPT GATES - SCRIPT-90S-VO.txt

script: SCRIPT-90S-VO.txt
generated: 2026-09-05T13:05:34+00:00
script_hash: d1c07a6b645c939834dd59230762136b6e650f38c13469f2feea0603779dc802
timing_source: measured

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/1, timing=estimated |
           opening gate: exit 1, 6/1/38/10 | screens: SCRIPT-90S-SCREENS.md, 16 items

VIEWER     SCRIPT-90S-VIEWER.md
  [FAIL ] V01 24/28 declared beats perceived (86%); unperceived: [stakes] w1, [rehook] w1, [rehook] w4, [ring] w9
  [WARN ] V04 1 window(s) with something unfollowable: 1:00-1:15 What “Tokyo’s tea break” refers to here.
  [PASS ] V02 no run of 2+ windows without a concrete new thing
  [PASS ] V03 open loop live in 10/10 windows (100%)
  [INFO ] V05 gain per window: median 3, 0 dead of 10 reported

## lint_script_pattern.py
exit 0

```
stats: {'sentence_mean': 11.3, 'sentence_count': 36, 'word_count': 406, 'rehook_positions_pct': [13, 47, 47, 72]}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-90S-VO.txt ===
             chars: 2384
         runtime_s: 144.4
           runtime: 2m 24s
         sentences: 36
     sentence_mean: 11.3
      break_ration: 0.84
  sentence_mean_carrying: 12.1
  short_figure_share: 8.3%
    sentence_stdev: 4.7
     over_20_share: 0.0%
       hook_spread: 13%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 7.5
       first_you_s: 5.9
         cta_count: 0
           rehooks: ['0.3m', '1.1m', '1.1m', '1.7m']
         phase_map: {'P1 OPEN': '0.0-0.3m', 'P2 ENGINE': '0.3-1.6m', 'P3 GAP': '0.4-1.1m', 'P4 PIVOT': '1.1-1.3m', 'P5 REFLECTION': '1.3-2.1m', 'P6 CLOSE': '0.9-2.4m'}
  p3_units_expected: 1
         a3_anchor: 0:14
         pivot_pct: None
     timing_source: estimated (no take on disk)

  [WARN] MAP sec 1: P1 computes to 19s; the open is pinned 60-90s at every runtime
  [INFO] estimator: the two rate estimates disagree by 13% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\tokyo-tea-break\SCRIPT-90S-GATES.md

RESULT: 0 FAIL, 1 WARN
```

## gate_opening_structure.py
exit 1

```
=== OPENING STRUCTURE GATE: SCRIPT-90S-VO.txt ===
           runtime: 1:21
            timing: measured (take)
          geometry: P1 0:00-0:35 (beat 5 from 0:23), P2 -1:05 (phase guides)
     density_bands: loops (2, 3), new-info (4, 6)
         a3_anchor: 0:08
             cycle: checked 0:00-1:21; longest gap 7s from 1:07
      unit_windows: ['P3 unit 1 0:13-0:36', 'P5 unit 2 0:44-1:10']
      counterparty: Japan
              ring: tea break
         packaging: title=None thumb=None thumb_file=None
    not_gated_here: Truby Battle / Self-Revelation / New Equilibrium, Snyder midpoint, chiastic center, ring CLOSE (P4-P6)
    beats_declared: {'ring': ['0:02', '1:18'], 'archetype': ['0:07'], 'stakes': ['0:14'], 'rehook': ['0:18', '1:01', '1:18'], 'opponent': ['0:20'], 'reflect': ['0:24', '1:05'], 'tricolon': ['0:29'], 'desire': ['0:32'], 'map': ['0:35'], 'payoff': ['0:38'], 'new': ['0:38', '0:47', '0:56', '1:07'], 'promise': ['0:41'], 'foreshadow': ['0:41'], 'catalyst': ['0:47'], 'head-fake': ['0:52'], 'debate': ['0:56'], 'loop': ['0:56', '1:07'], 'signpost': ['1:14'], 'loop-close': ['1:18'], 'dip': ['1:18']}

  [FAIL ] G02 first word at 0.00s in the edit clock
          Humes pre-opener, bent visual: the plate breathes 0.5-0.8s before the first word (38 B1 / doc 32 s7)
  [FAIL ] G15b 'tea break' never returns in the last 12% (1:11+)
          Ring MECHANISM: the claim planted with the token in P1 recurs in the close (47 s2 G-g)
  [FAIL ] G21 1 [loop] in P2
          L2 loops: 2-3 micro-loop closes at this runtime (P2 geometry / MAP s0)
  [FAIL ] G22 3 [new] in P2
          PLATFORM density: 4-6 new-info beats at this runtime (P2 geometry)
  [FAIL ] G37 no [archetype] declared in 0:08-0:30
          Truby Weakness/Need planted AS PEOPLE: an archetype-in-a-setting enters 0:08-0:30 (38 B3 / MAP s3)
  [FAIL ] G39 no [map] declared in beat 5
          Auditory handrail: map-not-territory signpost - tease the WHAT, hold the HOW (38 B5 / doc 32 s1)
  [WARN ] G31 0 dabs for 1 loops
          Glass alternation, P2 70/30: two loops with no reflection = listing (P2)
  [PASS ] G01 first sentence 2.76s
          PLATFORM 3s microhook (38 B1 / P1 QC)
  [PASS ] G03 paid at 7.59s, settle at 7.59s
          McKee gap paid WRONG by 0:08 + Humes post-key ON the boundary (38 B2)
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:02
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G06 clean
          Biography as the twist - AFTER the paradox, never before (38 B3)
  [PASS ] G07 [stakes] at 0:14
          Hook anatomy: stakes named by ~0:25 (38 B3)
  [PASS ] G08 [payoff] at 0:38
          One Minute Wall: real value FIRST, before the ask (38 B4)
  [PASS ] G09 promise at 0:41
          F1 + A1 + macro-loop-1 SETUP: the dated promise in 0:30-0:45 (38 B4 / MAP s3 / CLK; E24 roadmap by 0:45)
  [PASS ] G10 placed
          Humes pre-key immediately before the promise (P1 pause marks)
  [PASS ] G11 'In sixty seconds, you'll calculate the number that tracks their return'
          The promise carries a date or number and is calculable (38 B4 / doc 35)
  [PASS ] G12 1 declared in P1
          Rhetoric: ONE tricolon on the thesis line, none elsewhere in P1 (P1 B4 / doc 32 s3)
  [PASS ] G13 A2 at 1:01
          PLATFORM rehook A2 ~1:00, template family (38 B5 / P1 QC)
  [PASS ] G14 [opponent] at 0:20
          Truby Opponent / McKee antagonism: the opponent named, a MECHANISM never a villain (38 B5)
  [PASS ] G15 'tea break' planted at 0:00
          Ring composition: the ring token PLANTED in P1 (38 B5 / doc 32 s5)
  [PASS ] G16 1 [reflect] in P1
          Glass alternation, P1 80/20: exactly ONE reflection dab (P1)
  [PASS ] G17 clean
          HARD GATE attribution-first; [verify] never in hook/promise (P1/P2 / doc 32 s1)
  [PASS ] G18 1 marks in P1 (1.7/min)
          Humes pauses rationed: ~three per minute maximum (P1)
  [PASS ] G19 closed by [loop] at 0:56
          The catalyst is a micro loop CLOSED inside 30-60s, not exposition (P2)
  [PASS ] G20 longest gap 9s
          PLATFORM new-info cadence: something genuinely new every 15-30s (P2)
  [PASS ] G23 clean
          McKee gap, sentence-level: BUT/THEREFORE only - zero AND-THEN chains (P2 / doc 32 s4)
  [PASS ] G24 [head-fake] at 0:52
          Truby Plan v1 / head-fake #1 planted STRAIGHT, early-mid P2 (P2 MANDATORY / MAP s4)
  [PASS ] G25 A3 at 0:18
          PLATFORM rehook A3 at ~10% of runtime = 0:08 (P2 / MAP s4 QC; audit and gate share kit_spec.a3_anchor_s, E23)
  [PASS ] G26 [foreshadow] at 0:41
          Foreshadow schedule F2 at ~10%: the promise sighted again, none of it delivered (P2 / MAP s2)
  [PASS ] G27 'tea break' 1x in P2
          Ring composition: token TOUCHED exactly once in P2, unresolved (P2 / doc 32 s5)
  [PASS ] G28 [loop-close] at 1:18
          Macro loop 1 CLOSES on a partial answer that opens the bigger question (P2 / MAP s4, LIFO ledger)
  [PASS ] G29 [dip] at 1:18
          PLATFORM breathing dip IMMEDIATELY after the macro close - 2-3 beats of room tone (P2)
  [PASS ] G30 none
          PLATFORM: the ONLY mid-video CTA slot is the 15-30s after the macro payoff (P2)
  [PASS ] G32 tricolon 0, anaphora P1 0 / P2 0
          Rhetoric: ONE momentum tricolon max in P2; anaphora (if debuted in P1) recurs exactly once (P2 / doc 32 s3)
  [PASS ] G33 1 marks in P2
          Humes pauses in P2: no [pre-key] before the head-fake (that pause belongs to the pivot); <=3 marks in the phase
  [PASS ] G34 clean
          U6 / E20 concession budget: an agreement run never exceeds 2 sentences or 10s without a claim of ours
  [PASS ] G35 clean
          U6 / E20: a delivered proof is never hedged in the next sentence
  [PASS ] G36 longest stretch without a cycle beat: 7s from 1:07
          CLK the cycle repeats per beat - hook / show it's worth it / promise more / deliver; no >60s without a cycle beat, 0:00-1:21 (E23: whole runtime)
  [PASS ] G38 [desire] at 0:32
          Truby Desire named: the goal the video pursues (38 B5)
  [PASS ] G40 [catalyst] at 0:47
          Snyder Catalyst / McKee inciting incident: lands as a story beat in P2's first ~60s (P2)
  [PASS ] G41 [debate] at 0:56
          Snyder Debate / Truby Plan v1 FAILS: the obvious answer tried and found wanting, after the head-fake, mid-late P2 (P2 / MAP s4)
  [PASS ] G42 [signpost] at 1:14
          Auditory handrail: exit P2 on a transition signpost into the Gap (P2 / doc 32 s1)
  [PASS ] G43 2/3 declared beats open on a gap/consequence connector
          McKee gap: beats connect by BUT/THEREFORE - a beat that could swap places is filler (P2 / doc 32 s4)
  [PASS ] G44 all 2 unit windows rehook out
          PLATFORM rehook per unit: one template-family line or [rehook] inside every P3/P5 unit window (P3.md u5 / P5 / MAP s9 '1 per unit'; E23)
  [INFO ] G45 no --title given, G45 not run
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [JUDGE] J01 read the [opponent] line at 0:20
          McKee antagonism: the opponent is a mechanism, not a villain
  [JUDGE] J02 read the line at 0:52
          P2: the head-fake is offered STRAIGHT, no wink; demolition reserved for the pivot
  [JUDGE] J03 'Tokyo took a tea break on American debt.'
          Rhetoric: microhook concrete, terminal stress on the surprising word (38 B1)
  [JUDGE] J04 read P1 B5 and the P2 catalyst
          38 B5 context-dump ban: every abstraction cashed into an object or number within one sentence
  [JUDGE] J05 'Tokyo took a tea break on American debt.' -> 'And left Washington holding an unfunded bar tab wh'
          McKee: the gap opens - line 2 violates line 1's expected consequence (38 B1-B2)
  [JUDGE] J06 P1
          A/V irony counterpoint: the image TENSIONS the line, never illustrates it (38 B1 / doc 32 s6) - check the plate plan
  [JUDGE] J07 P2
          A/V contextual mapping: plates carry the archive, the voice carries motive and cost; a line that captions its visual fails (P2 / doc 32 s6) - check the plate plan
  [JUDGE] J08 read the promise line
          Rhetoric: phonetic anchor only on the promise/payoff/tell (doc 32 s3)
  [JUDGE] J11 read the line at 0:56
          McKee: the plan fails as a GAP (an action whose result violates expectation), never as a lecture
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'Tokyo took a tea break on American debt.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it

RESULT: 6 FAIL / 1 WARN / 38 PASS / 10 JUDGE (read these) / 1 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-90S-SCREENS.md: X1=5 deixis=3 junctions=1 anchors=7 declared=28
```

VERDICT: FAIL (1 failing tools, 1 viewer)
