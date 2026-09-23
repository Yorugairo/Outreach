# SCRIPT GATES - SCRIPT-B-VO.txt

script: SCRIPT-B-VO.txt
generated: 2026-09-16T05:26:41+00:00
script_hash: c30f08af1ee69f5ceb4240d49e422ce233b528650103746597316f690647ea68
timing_source: estimated

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/3, timing=estimated |
           opening gate: exit 0, 0/1/12/3 | screens: SCRIPT-B-SCREENS.md, 8 items

VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script            names the VIEWER block in its own acceptance)

## lint_script_pattern.py
exit 0

```
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 9.5, 'sentence_count': 18, 'word_count': 171, 'rehook_positions_pct': []}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-B-VO.txt ===
             chars: 1018
         runtime_s: 61.3
           runtime: 1m 01s
         sentences: 18
     sentence_mean: 9.5
      break_ration: 0.98
  sentence_mean_carrying: 9.5
  short_figure_share: 0.0%
    sentence_stdev: 2.1
     over_20_share: 0.0%
       hook_spread: 28%
   hook_properties: present-tense=y, viewer-facing=y
         paradox_s: 5.1
       first_you_s: 0.9
         cta_count: 0
           rehooks: []
         phase_map: {'P1 OPEN': '0.0-0.1m', 'P2 ENGINE': '0.1-1.4m', 'P3 GAP': '0.2-0.5m', 'P4 PIVOT': '0.5-0.6m', 'P5 REFLECTION': '0.6-0.9m', 'P6 CLOSE': '-0.5-1.0m'}
  p3_units_expected: 1
         a3_anchor: 0:06
         pivot_pct: None
              mode: short (G2)
     timing_source: estimated (no take on disk)

  [WARN] doc 32 sec 1 / doc 33: sentence mean 9.5 words (excluding sub-5-word figures) is outside the 10-15 band for speech; raw mean 9.5
  [WARN] doc 32 sec 1: sentence-length spread 2.1 is flat (min 3.5) — doctrine wants 5-word punches mixed with 15-word carries, not an even cadence
  [WARN] MAP sec 2: no rehook construction within 45s of anchor(s) A1, A2, A3 (A1 ~0:30, A2 ~1:00, A3 ~0:06 at 1:01 = 10% of runtime) — found at none
  [INFO] estimator: the two rate estimates disagree by 28% on the first sentence (numerals read longer than they look) — record a take to settle it
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\ai-slower-useful-faster\SCRIPT-B-GATES.md
  [INFO] MAP sec 1: short (G2): P1 computes to 8s; the 60-90s open is long-form geometry and does not bind
  [INFO] doc 35 rule 2: short (G2): no late-stage flip is asked of a short - the long form carries the tell

RESULT: 0 FAIL, 3 WARN
```

## gate_opening_structure.py
exit 0

```
=== OPENING STRUCTURE GATE: SCRIPT-B-VO.txt ===
              mode: short (G2: doc 51 s51.2)
           runtime: 1:00
            timing: estimated
         mechanism: Less supervision means more finished work from models we alr
         instances: 2
   ring_close_from: 0:48
        first_page: -
    beats_declared: {'ring': ['0:00', '0:57'], 'post-key': ['0:05'], 'new': ['0:20', '0:34'], 'stakes': ['0:29'], 'rehook': ['0:32'], 'catalyst': ['0:34'], 'reflect': ['0:50']}

  [WARN ] G48 1 publication-relative anchor(s) - re-screen each at publish and at any re-upload (a re-upload is a new assertion date): 0:16 'today' in 'I'd put the freed-up effort into making today's models finis'
          Perishable time anchors: every publication-relative phrase ('this week', 'last month', 'yesterday', 'two weeks ago', 'right now', 'this year') listed with its clock and re-screened at publish and at any re-upload - a false time anchor is the same class of defect as a false figure (C09-R013, ledger 8eb3d01c6196, 7e61f43b1162: 'a re-upload renews them at today's date.')
  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:00
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G45 title-word proxy: ['ai'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] G47 no self-referential runtime claim
          A script's promises about itself: a self-referential runtime ('the next eight minutes', 'this ten-minute video') agrees with the clock within max(60 s, 15%) - FAIL on a measured take, WARN on the estimate; a deadline ('in the next N minutes') breaks only past the end (C03-R011, ledger e319a9d02fe4: 'The script promised eight minutes and ran twelve.')
  [PASS ] G47b no counted promise with named items to check it against
          A script's promises about itself: a counted promise ('the five', 'three questions') agrees with the items the script names - the nearest named list, or the ordinals it walks - heuristic, so WARN (C03-R011, ledger e319a9d02fe4: 'A viewer counts four and then hears five.')
  [PASS ] S01 first sentence 2.12s
          51.2 HOOK 0:00-0:03: the claim, spoken and on screen, no throat-clearing
  [PASS ] S02 [post-key] sentence ends at 9.11s: 'Less supervision means more finished work from models we already have.'
          51.2 THE MECHANISM by 0:10: the one thing this short is about, stated plainly - declared with [post-key]
  [PASS ] S03 2 instance(s) at 0:20, 0:34
          51.2 N INSTANCES 0:10-0:52: the same mechanism N times, different variables ([new] / [catalyst])
  [PASS ] S05 'job' returns at the close sharing ['ai', 'second']
          51.2 THE RING in the last 20%: return to the mechanism, not to a phrase (G-g)
  [PASS ] S06 1 rehooks; no gap over 30 s
          CLK on a short: a rehook (template line or [rehook]) every 30 s, 0:00 to the end
  [PASS ] S07 clean
          the brand line ('Not a panic. Not a plot. Mechanics.') is stitched under the outro card - a script that speaks it doubles it
  [PASS ] S08 longest sentence 13 words: 'I'd put the freed-up effort into making today's models finish the job.'
          doc 37 speech: sentences 10-15 words; over 18 is several caption pages of one breath
  [JUDGE] J12 no --thumb-file given - open the FINAL thumbnail; sentence 1: 'AI can give you a second job.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J50 5s 'Less supervision means more finished work from models we alr'
          51.1 exactly ONE mechanism (49 s49.6 cognitive atomicity) - [post-key] is a delivery mark and may settle more than one key line: read the key lines as one mechanism or not
  [JUDGE] J51 0:20 shares nothing by stem; 0:34 shares nothing by stem
          51.2 the spine: 'if it is a list, the items must be one mechanism N times' (46 s46.4, G-g) - read each instance against the mechanism

RESULT: 0 FAIL / 1 WARN / 12 PASS / 3 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-B-SCREENS.md: X1=1 deixis=0 junctions=1 anchors=6 declared=8
```

VERDICT: PASS
