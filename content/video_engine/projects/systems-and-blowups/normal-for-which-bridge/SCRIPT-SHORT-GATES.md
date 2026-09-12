# SCRIPT GATES - SCRIPT-SHORT-VO.txt

script: SCRIPT-SHORT-VO.txt
generated: 2026-09-12T16:53:16+00:00
script_hash: 7940426b3cedda3f5dcf53048d1d1019cfc7bb4c4aaeb6ead8476a5ba1d00144
timing_source: measured

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/1, timing=estimated |
           opening gate: exit 0, 0/0/10/3 | screens: SCRIPT-SHORT-SCREENS.md, 7 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 9.1, 'sentence_count': 18, 'word_count': 164, 'rehook_positions_pct': []}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-SHORT-VO.txt ===
             chars: 917
         runtime_s: 56.9
           runtime: 0m 56s
         sentences: 18
     sentence_mean: 9.1
      break_ration: 1.09
  sentence_mean_carrying: 10.4
  short_figure_share: 16.7%
    sentence_stdev: 4.7
     over_20_share: 0.0%
       hook_spread: 1%
   hook_properties: present-tense=n, viewer-facing=n
         paradox_s: 7.6
       first_you_s: 8.3
         cta_count: 0
           rehooks: []
         phase_map: {'P1 OPEN': '0.0-0.1m', 'P2 ENGINE': '0.1-1.4m', 'P3 GAP': '0.2-0.4m', 'P4 PIVOT': '0.4-0.5m', 'P5 REFLECTION': '0.5-0.8m', 'P6 CLOSE': '-0.6-0.9m'}
  p3_units_expected: 1
         a3_anchor: 0:05
         pivot_pct: None
              mode: short (G2)
     timing_source: estimated (no take on disk)

  [WARN] MAP sec 2: no rehook construction within 45s of anchor(s) A1, A2, A3 (A1 ~0:30, A2 ~1:00, A3 ~0:05 at 0:56 = 10% of runtime) — found at none
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\normal-for-which-bridge\SCRIPT-SHORT-GATES.md
  [INFO] MAP sec 1: short (G2): P1 computes to 7s; the 60-90s open is long-form geometry and does not bind
  [INFO] doc 35 rule 2: short (G2): no late-stage flip is asked of a short - the long form carries the tell

RESULT: 0 FAIL, 1 WARN
```

## gate_opening_structure.py
exit 0

```
=== OPENING STRUCTURE GATE: SCRIPT-SHORT-VO.txt ===
              mode: short (G2: doc 51 s51.2)
           runtime: 1:09
            timing: measured
         mechanism: But a yield is a weight, not a number, and the bridge under 
         instances: 6
   ring_close_from: 0:55
        first_page: 0.00s
    beats_declared: {'ring': ['0:00', '0:58'], 'post-key': ['0:03'], 'stakes': ['0:03'], 'rehook': ['0:09', '0:19', '0:37', '0:44'], 'new': ['0:15', '0:26', '0:37', '0:41', '0:49'], 'catalyst': ['0:30'], 'reflect': ['0:49']}

  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:09
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G45 title-word proxy: ['five', 'percent', 'normal'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] S01 first sentence 2.30s
          51.2 HOOK 0:00-0:03: the claim, spoken and on screen, no throat-clearing
  [PASS ] S02 [post-key] sentence ends at 8.88s: 'But a yield is a weight, not a number, and the bridge under it is four'
          51.2 THE MECHANISM by 0:10: the one thing this short is about, stated plainly - declared with [post-key]
  [PASS ] S03 6 instance(s) at 0:15, 0:26, 0:30, 0:37, 0:41, 0:49
          51.2 N INSTANCES 0:10-0:55: the same mechanism N times, different variables ([new] / [catalyst])
  [PASS ] S05 'normal' returns at the close sharing ['five', 'percent']
          51.2 THE RING in the last 20%: return to the mechanism, not to a phrase (G-g)
  [PASS ] S06 4 rehooks; no gap over 30 s
          CLK on a short: a rehook (template line or [rehook]) every 30 s, 0:00 to the end
  [PASS ] S07 clean
          the brand line ('Not a panic. Not a plot. Mechanics.') is stitched under the outro card - a script that speaks it doubles it
  [PASS ] S08 longest sentence 18 words: 'But a yield is a weight, not a number, and the bridge under it is four'
          doc 37 speech: sentences 10-15 words; over 18 is several caption pages of one breath
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'Five percent was normal once.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J50 3s 'But a yield is a weight, not a number, and the bridge under '
          51.1 exactly ONE mechanism (49 s49.6 cognitive atomicity) - [post-key] is a delivery mark and may settle more than one key line: read the key lines as one mechanism or not
  [JUDGE] J51 0:15 shares ['four']; 0:26 shares ['bridge', 'number']; 0:30 shares nothing by stem; 0:37 shares nothing by stem; 0:41 shares nothing by stem; 0:49 shares ['number']
          51.2 the spine: 'if it is a list, the items must be one mechanism N times' (46 s46.4, G-g) - read each instance against the mechanism

RESULT: 0 FAIL / 0 WARN / 10 PASS / 3 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-SHORT-SCREENS.md: X1=1 deixis=1 junctions=0 anchors=5 declared=14
```

VERDICT: PASS
