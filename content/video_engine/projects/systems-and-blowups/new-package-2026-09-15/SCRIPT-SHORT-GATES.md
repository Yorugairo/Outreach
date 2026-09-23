# SCRIPT GATES - SCRIPT-SHORT-VO.txt

script: SCRIPT-SHORT-VO.txt
generated: 2026-09-16T04:53:11+00:00
script_hash: afe66a92f9570ad78d7feda4cec7fb7642341a27ad59abde8ec7b161b15bca25
timing_source: estimated

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/3, timing=estimated |
           opening gate: exit 0, 0/0/13/3 | screens: SCRIPT-SHORT-SCREENS.md, 13 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 9.0, 'sentence_count': 16, 'word_count': 144, 'rehook_positions_pct': []}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-SHORT-VO.txt ===
             chars: 842
         runtime_s: 51.1
           runtime: 0m 51s
         sentences: 16
     sentence_mean: 9.0
      break_ration: 1.19
  sentence_mean_carrying: 9.0
  short_figure_share: 0.0%
    sentence_stdev: 2.3
     over_20_share: 0.0%
       hook_spread: 10%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 7.2
       first_you_s: 7.3
         cta_count: 0
           rehooks: []
         phase_map: {'P1 OPEN': '0.0-0.1m', 'P2 ENGINE': '0.1-1.4m', 'P3 GAP': '0.1-0.4m', 'P4 PIVOT': '0.4-0.5m', 'P5 REFLECTION': '0.5-0.7m', 'P6 CLOSE': '-0.6-0.9m'}
  p3_units_expected: 1
         a3_anchor: 0:05
         pivot_pct: None
              mode: short (G2)
     timing_source: estimated (no take on disk)

  [WARN] doc 32 sec 1 / doc 33: sentence mean 9.0 words (excluding sub-5-word figures) is outside the 10-15 band for speech; raw mean 9.0
  [WARN] doc 32 sec 1: sentence-length spread 2.3 is flat (min 3.5) — doctrine wants 5-word punches mixed with 15-word carries, not an even cadence
  [WARN] MAP sec 2: no rehook construction within 45s of anchor(s) A1, A2, A3 (A1 ~0:30, A2 ~1:00, A3 ~0:05 at 0:51 = 10% of runtime) — found at none
  [INFO] estimator: the two rate estimates disagree by 10% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\new-package-2026-09-15\SCRIPT-SHORT-GATES.md
  [INFO] MAP sec 1: short (G2): P1 computes to 7s; the 60-90s open is long-form geometry and does not bind
  [INFO] doc 35 rule 2: short (G2): no late-stage flip is asked of a short - the long form carries the tell

RESULT: 0 FAIL, 3 WARN
```

## gate_opening_structure.py
exit 0

```
=== OPENING STRUCTURE GATE: SCRIPT-SHORT-VO.txt ===
              mode: short (G2: doc 51 s51.2)
           runtime: 0:50
            timing: estimated
         mechanism: Lower rates can leave a bigger bill.
         instances: 4
   ring_close_from: 0:40
        first_page: -
    beats_declared: {'ring': ['0:00', '0:41'], 'post-key': ['0:00'], 'stakes': ['0:02'], 'new': ['0:10', '0:20', '0:34'], 'rehook': ['0:18', '0:31'], 'catalyst': ['0:22'], 'reflect': ['0:34']}

  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:07
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G45 title-word proxy: ['lower', 'rat', 'leave', 'bigger', 'bill'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] G47 no self-referential runtime claim
          A script's promises about itself: a self-referential runtime ('the next eight minutes', 'this ten-minute video') agrees with the clock within max(60 s, 15%) - FAIL on a measured take, WARN on the estimate; a deadline ('in the next N minutes') breaks only past the end (C03-R011, ledger e319a9d02fe4: 'The script promised eight minutes and ran twelve.')
  [PASS ] G47b no counted promise with named items to check it against
          A script's promises about itself: a counted promise ('the five', 'three questions') agrees with the items the script names - the nearest named list, or the ordinals it walks - heuristic, so WARN (C03-R011, ledger e319a9d02fe4: 'A viewer counts four and then hears five.')
  [PASS ] G48 no publication-relative time anchor
          Perishable time anchors: every publication-relative phrase ('this week', 'last month', 'yesterday', 'two weeks ago', 'right now', 'this year') listed with its clock and re-screened at publish and at any re-upload - a false time anchor is the same class of defect as a false figure (C09-R013, ledger 8eb3d01c6196, 7e61f43b1162: 'a re-upload renews them at today's date.')
  [PASS ] S01 first sentence 2.33s
          51.2 HOOK 0:00-0:03: the claim, spoken and on screen, no throat-clearing
  [PASS ] S02 [post-key] sentence ends at 2.33s: 'Lower rates can leave a bigger bill.'
          51.2 THE MECHANISM by 0:10: the one thing this short is about, stated plainly - declared with [post-key]
  [PASS ] S03 4 instance(s) at 0:10, 0:20, 0:22, 0:34
          51.2 N INSTANCES 0:10-0:43: the same mechanism N times, different variables ([new] / [catalyst])
  [PASS ] S05 'bill' returns at the close sharing ['bigger', 'leave']
          51.2 THE RING in the last 20%: return to the mechanism, not to a phrase (G-g)
  [PASS ] S06 2 rehooks; no gap over 30 s
          CLK on a short: a rehook (template line or [rehook]) every 30 s, 0:00 to the end
  [PASS ] S07 clean
          the brand line ('Not a panic. Not a plot. Mechanics.') is stitched under the outro card - a script that speaks it doubles it
  [PASS ] S08 longest sentence 15 words: 'A new loan can cost less than before, but more than the loan it replac'
          doc 37 speech: sentences 10-15 words; over 18 is several caption pages of one breath
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'Lower rates can leave a bigger bill.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J50 0s 'Lower rates can leave a bigger bill.'
          51.1 exactly ONE mechanism (49 s49.6 cognitive atomicity) - [post-key] is a delivery mark and may settle more than one key line: read the key lines as one mechanism or not
  [JUDGE] J51 0:10 shares nothing by stem; 0:20 shares nothing by stem; 0:22 shares nothing by stem; 0:34 shares nothing by stem
          51.2 the spine: 'if it is a list, the items must be one mechanism N times' (46 s46.4, G-g) - read each instance against the mechanism

RESULT: 0 FAIL / 0 WARN / 13 PASS / 3 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-SHORT-SCREENS.md: X1=4 deixis=4 junctions=0 anchors=5 declared=10
```

VERDICT: PASS
