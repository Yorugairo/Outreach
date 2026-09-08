# SCRIPT GATES - SCRIPT-SHORT-VO.txt

script: SCRIPT-SHORT-VO.txt
generated: 2026-09-07T17:33:53+00:00
script_hash: e93b0dfe6daccd1bed1fb64185c6cb977e6d8f4ff4db0c74d77c492d5b6fd82c
timing_source: estimated

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/0, timing=estimated |
           opening gate: exit 0, 0/0/10/3 | screens: SCRIPT-SHORT-SCREENS.md, 15 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
stats: {'sentence_mean': 10.5, 'sentence_count': 24, 'word_count': 252, 'rehook_positions_pct': [14, 44]}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-SHORT-VO.txt ===
             chars: 1506
         runtime_s: 90.5
           runtime: 1m 30s
         sentences: 24
     sentence_mean: 10.5
      break_ration: 0.66
  sentence_mean_carrying: 11.1
  short_figure_share: 8.3%
    sentence_stdev: 4.3
     over_20_share: 0.0%
       hook_spread: 2%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 8.8
       first_you_s: 13.7
         cta_count: 0
           rehooks: ['0.2m', '0.2m', '0.6m', '0.9m', '1.3m']
         phase_map: {'P1 OPEN': '0.0-0.2m', 'P2 ENGINE': '0.2-1.4m', 'P3 GAP': '0.3-0.7m', 'P4 PIVOT': '0.7-0.8m', 'P5 REFLECTION': '0.8-1.3m', 'P6 CLOSE': '0.0-1.5m'}
  p3_units_expected: 1
         a3_anchor: 0:09
         pivot_pct: None
              mode: short (G2)
     timing_source: estimated (no take on disk)

  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\japan-tariff-trick\SCRIPT-SHORT-GATES.md
  [INFO] MAP sec 1: short (G2): P1 computes to 12s; the 60-90s open is long-form geometry and does not bind
  [INFO] doc 35 rule 2: short (G2): no late-stage flip is asked of a short - the long form carries the tell

RESULT: 0 FAIL, 0 WARN
```

## gate_opening_structure.py
exit 0

```
=== OPENING STRUCTURE GATE: SCRIPT-SHORT-VO.txt ===
              mode: short (G2: doc 51 s51.2)
           runtime: 1:29
            timing: estimated
         mechanism: Instead, that tariff funded Japan's chip empire, and cost Am
         instances: 4
   ring_close_from: 1:11
    beats_declared: {'post-key': ['0:02'], 'rehook': ['0:08', '0:33', '0:45', '1:13'], 'new': ['0:13', '0:50'], 'archetype': ['0:23'], 'catalyst': ['0:30', '0:58'], 'ring': ['1:22']}

  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:13
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G45 title-word proxy: ['japan', 'trump'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] S01 first sentence 2.49s
          51.2 HOOK 0:00-0:03: the claim, spoken and on screen, no throat-clearing
  [PASS ] S02 [post-key] sentence ends at 8.76s: 'Instead, that tariff funded Japan's chip empire, and cost America a hu'
          51.2 THE MECHANISM by 0:10: the one thing this short is about, stated plainly - declared with [post-key]
  [PASS ] S03 4 instance(s) at 0:13, 0:30, 0:50, 0:58
          51.2 N INSTANCES 0:10-1:17: the same mechanism N times, different variables ([new] / [catalyst])
  [PASS ] S05 'tariff' returns at the close sharing ['america', 'chip', 'fund']
          51.2 THE RING in the last 20%: return to the mechanism, not to a phrase (G-g)
  [PASS ] S06 8 rehooks; no gap over 30 s
          CLK on a short: a rehook (template line or [rehook]) every 30 s, 0:00 to the end
  [PASS ] S07 clean
          the brand line ('Not a panic. Not a plot. Mechanics.') is stitched under the outro card - a script that speaks it doubles it
  [PASS ] S08 longest sentence 17 words: 'Instead, that tariff funded Japan's chip empire, and cost America a hu'
          doc 37 speech: sentences 10-15 words; over 18 is several caption pages of one breath
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'Trump announced he beat Japan on tariffs.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J50 2s 'Instead, that tariff funded Japan's chip empire, and cost Am'
          51.1 exactly ONE mechanism (49 s49.6 cognitive atomicity) - [post-key] is a delivery mark and may settle more than one key line: read the key lines as one mechanism or not
  [JUDGE] J51 0:13 shares nothing by stem; 0:30 shares nothing by stem; 0:50 shares nothing by stem; 0:58 shares ['billion', 'dollar', 'hundr', 'twenty', 'two']
          51.2 the spine: 'if it is a list, the items must be one mechanism N times' (46 s46.4, G-g) - read each instance against the mechanism

RESULT: 0 FAIL / 0 WARN / 10 PASS / 3 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-SHORT-SCREENS.md: X1=3 deixis=0 junctions=2 anchors=10 declared=10
```

VERDICT: PASS
