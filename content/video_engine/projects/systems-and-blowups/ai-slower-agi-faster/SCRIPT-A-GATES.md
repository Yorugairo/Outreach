# SCRIPT GATES - SCRIPT-A-VO.txt

script: SCRIPT-A-VO.txt
generated: 2026-09-16T05:53:52+00:00
script_hash: aab5fc4c98a281b4b0466ecb56cee351514bc9395810bef2411eb171ffc6516c
timing_source: estimated

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/1, timing=estimated |
           opening gate: exit 1, 3/1/9/3 | screens: SCRIPT-A-SCREENS.md, 14 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 10.4, 'sentence_count': 25, 'word_count': 260, 'rehook_positions_pct': []}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-A-VO.txt ===
             chars: 1527
         runtime_s: 92.5
           runtime: 1m 32s
         sentences: 25
     sentence_mean: 10.4
      break_ration: 0.65
  sentence_mean_carrying: 11.3
  short_figure_share: 12.0%
    sentence_stdev: 4.1
     over_20_share: 0.0%
       hook_spread: 21%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 3.6
       first_you_s: None
         cta_count: 0
           rehooks: []
         phase_map: {'P1 OPEN': '0.0-0.2m', 'P2 ENGINE': '0.2-1.4m', 'P3 GAP': '0.3-0.7m', 'P4 PIVOT': '0.7-0.8m', 'P5 REFLECTION': '0.8-1.3m', 'P6 CLOSE': '0.0-1.5m'}
  p3_units_expected: 1
         a3_anchor: 0:09
         pivot_pct: None
              mode: short (G2)
     timing_source: estimated (no take on disk)

  [WARN] MAP sec 2: no rehook construction within 45s of anchor(s) A1, A2, A3 (A1 ~0:30, A2 ~1:00, A3 ~0:09 at 1:32 = 10% of runtime) — found at none
  [INFO] estimator: the two rate estimates disagree by 21% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\ai-slower-agi-faster\SCRIPT-A-GATES.md
  [INFO] MAP sec 1: short (G2): P1 computes to 12s; the 60-90s open is long-form geometry and does not bind
  [INFO] doc 35 rule 2: short (G2): no late-stage flip is asked of a short - the long form carries the tell

RESULT: 0 FAIL, 1 WARN
```

## gate_opening_structure.py
exit 1

```
=== OPENING STRUCTURE GATE: SCRIPT-A-VO.txt ===
              mode: short (G2: doc 51 s51.2)
           runtime: 1:31
            timing: estimated
         mechanism: A bigger brain is only one part; memory, tools, and recovery
         instances: 3
   ring_close_from: 1:13
        first_page: -
    beats_declared: {'ring': ['0:01', '1:28'], 'post-key': ['0:06'], 'new': ['0:23', '0:28'], 'rehook': ['0:36', '0:43'], 'catalyst': ['0:46'], 'reflect': ['1:13']}

  [FAIL ] G05 no 'you' before 0:30
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [FAIL ] S02 [post-key] sentence ends at 11.40s; no scene timeline read (--scenes) so no page can carry it: 'A bigger brain is only one part; memory, tools, and recovery can carry'
          51.2 THE MECHANISM by 0:10: the one thing this short is about, stated plainly - declared with [post-key] or carried by the first ledger page (E44)
  [FAIL ] S06 2 rehooks; longest gap 0:00+37s, 0:43+48s
          CLK on a short: a rehook (template line or [rehook]) every 30 s, 0:00 to the end
  [WARN ] G45 title-word proxy: ['get', 'stuck'] only in sentence 2 - the first sentence should state the thesis the packaging implied
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G47 no self-referential runtime claim
          A script's promises about itself: a self-referential runtime ('the next eight minutes', 'this ten-minute video') agrees with the clock within max(60 s, 15%) - FAIL on a measured take, WARN on the estimate; a deadline ('in the next N minutes') breaks only past the end (C03-R011, ledger e319a9d02fe4: 'The script promised eight minutes and ran twelve.')
  [PASS ] G47b no counted promise with named items to check it against
          A script's promises about itself: a counted promise ('the five', 'three questions') agrees with the items the script names - the nearest named list, or the ordinals it walks - heuristic, so WARN (C03-R011, ledger e319a9d02fe4: 'A viewer counts four and then hears five.')
  [PASS ] G48 no publication-relative time anchor
          Perishable time anchors: every publication-relative phrase ('this week', 'last month', 'yesterday', 'two weeks ago', 'right now', 'this year') listed with its clock and re-screened at publish and at any re-upload - a false time anchor is the same class of defect as a false figure (C09-R013, ledger 8eb3d01c6196, 7e61f43b1162: 'a re-upload renews them at today's date.')
  [PASS ] S01 first sentence 1.25s
          51.2 HOOK 0:00-0:03: the claim, spoken and on screen, no throat-clearing
  [PASS ] S03 3 instance(s) at 0:23, 0:28, 0:46
          51.2 N INSTANCES 0:10-1:19: the same mechanism N times, different variables ([new] / [catalyst])
  [PASS ] S05 'stuck' returns at the close sharing ['get']
          51.2 THE RING in the last 20%: return to the mechanism, not to a phrase (G-g)
  [PASS ] S07 clean
          the brand line ('Not a panic. Not a plot. Mechanics.') is stitched under the outro card - a script that speaks it doubles it
  [PASS ] S08 longest sentence 18 words: 'When the model writes the plan, the tool executes it, and feedback red'
          doc 37 speech: sentences 10-15 words; over 18 is several caption pages of one breath
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'It writes the fix.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J50 6s 'A bigger brain is only one part; memory, tools, and recovery'
          51.1 exactly ONE mechanism (49 s49.6 cognitive atomicity) - [post-key] is a delivery mark and may settle more than one key line: read the key lines as one mechanism or not
  [JUDGE] J51 0:23 shares nothing by stem; 0:28 shares nothing by stem; 0:46 shares nothing by stem
          51.2 the spine: 'if it is a list, the items must be one mechanism N times' (46 s46.4, G-g) - read each instance against the mechanism

RESULT: 3 FAIL / 1 WARN / 9 PASS / 3 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-A-SCREENS.md: X1=4 deixis=3 junctions=1 anchors=6 declared=8
```

VERDICT: FAIL (1 failing tools)
