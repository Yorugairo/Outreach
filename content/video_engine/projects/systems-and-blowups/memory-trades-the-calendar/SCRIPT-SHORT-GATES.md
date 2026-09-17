# SCRIPT GATES - SCRIPT-SHORT-VO.txt

script: SCRIPT-SHORT-VO.txt
generated: 2026-09-17T03:57:32+00:00
script_hash: 36abab6f33119e1cdb2d6ef5df69867c0111dfb31c40e88715a417a71ead306e
timing_source: measured

TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/2, timing=measured |
           opening gate: exit 0, 0/0/13/3 | screens: SCRIPT-SHORT-SCREENS.md, 6 items

VIEWER     SCRIPT-SHORT-VIEWER.md  (advisory: --no-viewer-gate - these rows do not change the VERDICT)
  [INFO ] V01 6/8 declared beats perceived (75%); unperceived: [rehook] w1, [rehook] w4
  [INFO ] V02 no run of 2+ windows without a concrete new thing
  [INFO ] V03 open loop live in 5/5 windows (100%)
  [INFO ] V04 nothing the reader could not follow
  [INFO ] V05 gain per window: median 4, 0 dead of 5 reported

## lint_script_pattern.py
exit 0

```
WARN REHOOK: no rehook-family construction found
stats: {'sentence_mean': 8.3, 'sentence_count': 28, 'word_count': 232, 'rehook_positions_pct': []}
RESULT: clean
```

## audit_script_doctrine.py
exit 0

```
=== SCRIPT-SHORT-VO.txt ===
             chars: 1285
         runtime_s: 80.2
           runtime: 1m 20s
         sentences: 28
     sentence_mean: 8.3
      break_ration: 0.78
  sentence_mean_carrying: 9.3
  short_figure_share: 17.9%
    sentence_stdev: 4.3
     over_20_share: 0.0%
       hook_spread: 2%
   hook_properties: present-tense=y, viewer-facing=n
         paradox_s: 3.6
       first_you_s: 10.1
         cta_count: 0
           rehooks: []
         phase_map: {'P1 OPEN': '0.0-0.2m', 'P2 ENGINE': '0.2-1.4m', 'P3 GAP': '0.2-0.6m', 'P4 PIVOT': '0.6-0.7m', 'P5 REFLECTION': '0.7-1.2m', 'P6 CLOSE': '-0.2-1.3m'}
  p3_units_expected: 1
         a3_anchor: 0:08
         pivot_pct: None
              mode: short (G2)
     timing_source: measured (225 words on disk)
   hook_measured_s: 2.38
  paradox_measured_s: 4.14

  [WARN] doc 32 sec 1 / doc 33: sentence mean 9.3 words (excluding sub-5-word figures) is outside the 10-15 band for speech; raw mean 8.3
  [WARN] MAP sec 2: no rehook construction within 45s of anchor(s) A1, A2, A3 (A1 ~0:30, A2 ~1:00, A3 ~0:08 at 1:20 = 10% of runtime) — found at none
  [INFO] doc 38 B1-B4: owned by gate_opening_structure - see content\video_engine\projects\systems-and-blowups\memory-trades-the-calendar\SCRIPT-SHORT-GATES.md
  [INFO] MAP sec 1: short (G2): P1 computes to 10s; the 60-90s open is long-form geometry and does not bind
  [INFO] doc 35 rule 2: short (G2): no late-stage flip is asked of a short - the long form carries the tell

RESULT: 0 FAIL, 2 WARN
```

## gate_opening_structure.py
exit 0

```
=== OPENING STRUCTURE GATE: SCRIPT-SHORT-VO.txt ===
              mode: short (G2: doc 51 s51.2)
           runtime: 1:11
            timing: measured
         mechanism: They trade the calendar.
         instances: 4
   ring_close_from: 0:57
        first_page: -
    beats_declared: {'post-key': ['0:02'], 'rehook': ['0:15', '0:43'], 'new': ['0:24', '0:34', '0:51'], 'catalyst': ['0:43'], 'ring': ['1:09']}

  [PASS ] G04 clean
          PLATFORM ban list: no greeting, no 'in this video', no channel talk (38 B2)
  [PASS ] G05 'you' at 0:09
          Direct address: 'you' by 0:30 (38 B3 / doc 32 s1)
  [PASS ] G45 title-word proxy: ['memory', 'stock', 'trade', 'new'] echoed in sentence 1
          E24 / doc 29 s9.29: proxy for 'the first sentence answers the thumbnail' - the title is the words packaged with it
  [PASS ] G47 no self-referential runtime claim
          A script's promises about itself: a self-referential runtime ('the next eight minutes', 'this ten-minute video') agrees with the clock within max(60 s, 15%) - FAIL on a measured take, WARN on the estimate; a deadline ('in the next N minutes') breaks only past the end (C03-R011, ledger e319a9d02fe4: 'The script promised eight minutes and ran twelve.')
  [PASS ] G47b no counted promise with named items to check it against
          A script's promises about itself: a counted promise ('the five', 'three questions') agrees with the items the script names - the nearest named list, or the ordinals it walks - heuristic, so WARN (C03-R011, ledger e319a9d02fe4: 'A viewer counts four and then hears five.')
  [PASS ] G48 no publication-relative time anchor
          Perishable time anchors: every publication-relative phrase ('this week', 'last month', 'yesterday', 'two weeks ago', 'right now', 'this year') listed with its clock and re-screened at publish and at any re-upload - a false time anchor is the same class of defect as a false figure (C09-R013, ledger 8eb3d01c6196, 7e61f43b1162: 'a re-upload renews them at today's date.')
  [PASS ] S01 first sentence 2.38s
          51.2 HOOK 0:00-0:03: the claim, spoken and on screen, no throat-clearing
  [PASS ] S02 [post-key] sentence ends at 4.14s: 'They trade the calendar.'
          51.2 THE MECHANISM by 0:10: the one thing this short is about, stated plainly - declared with [post-key]
  [PASS ] S03 4 instance(s) at 0:24, 0:34, 0:43, 0:51
          51.2 N INSTANCES 0:10-0:57: the same mechanism N times, different variables ([new] / [catalyst])
  [PASS ] S05 'calendar' returns at the close sharing ['trade']
          51.2 THE RING in the last 20%: return to the mechanism, not to a phrase (G-g)
  [PASS ] S06 2 rehooks; no gap over 30 s
          CLK on a short: a rehook (template line or [rehook]) every 30 s, 0:00 to the end
  [PASS ] S07 clean
          the brand line ('Not a panic. Not a plot. Mechanics.') is stitched under the outro card - a script that speaks it doubles it
  [PASS ] S08 longest sentence 18 words: 'You have to know the calendar: the day the print lands is the day the '
          doc 37 speech: sentences 10-15 words; over 18 is several caption pages of one breath
  [JUDGE] J12 open content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar/thumbnails/thumb-01-trade-the-calendar.png; sentence 1: 'Memory stocks don't trade the news.'
          E24 / doc 29 s9.29: the first sentence answers what the thumbnail poses - open the thumbnail and read sentence 1 against it
  [JUDGE] J50 3s 'They trade the calendar.'
          51.1 exactly ONE mechanism (49 s49.6 cognitive atomicity) - [post-key] is a delivery mark and may settle more than one key line: read the key lines as one mechanism or not
  [JUDGE] J51 0:24 shares nothing by stem; 0:34 shares nothing by stem; 0:43 shares nothing by stem; 0:51 shares nothing by stem
          51.2 the spine: 'if it is a list, the items must be one mechanism N times' (46 s46.4, G-g) - read each instance against the mechanism

RESULT: 0 FAIL / 0 WARN / 13 PASS / 3 JUDGE (read these) / 0 INFO
```

## enumerate_strength_screens.py
exit 0

```
SCRIPT-SHORT-SCREENS.md: X1=2 deixis=0 junctions=0 anchors=4 declared=7
```

VERDICT: PASS
