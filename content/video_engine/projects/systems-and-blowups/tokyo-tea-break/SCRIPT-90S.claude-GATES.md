# SCRIPT GATES - SCRIPT-90S-VO.claude.txt

script: SCRIPT-90S-VO.claude.txt
generated: 2026-09-05T22:54:48+00:00
script_hash: 79fc80ceff9df48f52a71f165ef53995f60ed3bc519a3ee629b0f4d948c6eaf4
timing_source: measured

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/0, timing=estimated |
           opening gate: exit 0, 0/1/9/3 | screens: SCRIPT-90S.claude-SCREENS.md, 5 items

VIEWER     SCRIPT-90S.claude-VIEWER.md
  [FAIL ] V01 21/24 declared beats perceived (88%); unperceived: [stakes] w0, [promise] w2, [rehook] w2
  [WARN ] V04 1 window(s) with something unfollowable: 0:00-0:15 What “Tokyo took a tea break” means
  [PASS ] V02 no run of 2+ windows without a concrete new thing
  [PASS ] V03 open loop live in 6/7 windows (86%)
  [INFO ] V05 gain per window: median 4, 0 dead of 7 reported

## lint_script_pattern.py
exit 0

```
stats: {'sentence_mean': 12.0, 'sentence_count': 20, 'word_count': 240, 'rehook_positions_pct': [20, 73]}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-90S-VO.claude.txt ===
             chars: 1329
         runtime_s: 82.9
           runtime: 1m 22s
         sentences: 20
     sentence_mean: 12.0
      break_ration: 2.26
  sentence_mean_carrying: 12.0
  short_figure_share: 0.0%
    sentence_stdev: 5.4
     over_20_share: 5.0%
       hook_spread: 20%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 4.3
       first_you_s: 6.0
         cta_count: 0
           rehooks: ['0.3m', '1.0m']
         phase_map: {'P1 OPEN': '0.0-0.2m', 'P2 ENGINE': '0.2-1.4m', 'P3 GAP': '0.2-0.6m', 'P4 PIVOT': '0.6-0.8m', 'P5 REFLECTION': '0.8-1.2m', 'P6 CLOSE': '-0.1-1.4m'}
  p3_units_expected: 1
         a3_anchor: 0:08
         pivot_pct: None
              mode: short (G2)
     timing_source: estimated (no take on disk)

  [INFO] estimator: the two rate estimates disagree by 20% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see projects\systems-and-blowups\tokyo-tea-break\SCRIPT-90S.claude-GATES.md
  [INFO] MAP sec 1: short (G2): P1 computes to 11s; the 60-90s open is long-form geometry and does not bind
  [INFO] doc 35 rule 2: short (G2): no late-stage flip is asked of a short - the long form carries the tell

RESULT: 0 FAIL, 0 WARN
```

## gate_opening_structure.py
exit 0

```
=== OPENING STRUCTURE GATE: SCRIPT-90S-VO.claude.txt ===
              mode: short (G2: doc 51 s51.2)
           runtime: 1:22
            timing: measured
         mechanism: And left America with an unfunded bar tab.
         instances: 5
   ring_close_from: 1:06
    beats_declared: {'post-key': ['0:01', '0:59'], 'stakes': ['0:05'], 'archetype': ['0:05'], 'tricolon': ['0:09'], 'rehook': ['0:14', '0:41', '0:59'], 'payoff': ['0:17'], 'new': ['0:21', '0:45', '0:50', '0:55'], 'reflect': ['0:21'], 'opponent': ['0:27'], 'desire': ['0:33'], 'map': ['0:36'], 'pre-key': ['0:36'], 'promise': ['0:41'], 'catalyst': ['0:41'], 'loop': ['0:45', '0:50'], 'foreshadow': ['0:50'], 'loop-close': ['0:55'], 'dip': ['1:05'], 'signpost': ['1:05'], 'ring': ['1:18']}

  [WARN ] S08 longest sentence 27 words: 'Pull up Meta and find its price-to-earnings multiple: that's the share'
          doc 37 speech: sentences 10-15 words; over 18 is several caption pages of one breath
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:05
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G45 title-word proxy: ['tokyo', 'tea', 'break'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] S01 first sentence 1.45s
          51.2 HOOK 0:00-0:03: the claim, spoken and on screen, no throat-clearing
  [PASS ] S02 [post-key] sentence ends at 4.74s: 'And left America with an unfunded bar tab.'
          51.2 THE MECHANISM by 0:10: the one thing this short is about, stated plainly - declared with [post-key]
  [PASS ] S03 5 instance(s) at 0:21, 0:41, 0:45, 0:50, 0:55
          51.2 N INSTANCES 0:10-1:06: the same mechanism N times, different variables ([new] / [catalyst])
  [PASS ] S05 'tea break' returns at the close sharing ['tokyo']
          51.2 THE RING in the last 20%: return to the mechanism, not to a phrase (G-g)
  [PASS ] S06 4 rehooks; no gap over 30 s
          CLK on a short: a rehook (template line or [rehook]) every 30 s, 0:00 to the end
  [PASS ] S07 clean
          the brand line ('Not a panic. Not a plot. Mechanics.') is stitched under the outro card - a script that speaks it doubles it
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'Tokyo took a tea break.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J50 2s 'And left America with an unfunded bar tab.'; 60s 'And here's what nobody says: the money went home, and the ta'
          51.1 exactly ONE mechanism (49 s49.6 cognitive atomicity) - [post-key] is a delivery mark and may settle more than one key line: read the key lines as one mechanism or not
  [JUDGE] J51 0:21 shares nothing by stem; 0:41 shares nothing by stem; 0:45 shares nothing by stem; 0:50 shares nothing by stem; 0:55 shares nothing by stem
          51.2 the spine: 'if it is a list, the items must be one mechanism N times' (46 s46.4, G-g) - read each instance against the mechanism

RESULT: 0 FAIL / 1 WARN / 9 PASS / 3 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-90S.claude-SCREENS.md: X1=1 deixis=0 junctions=1 anchors=3 declared=24
```

VERDICT: FAIL (1 viewer)
