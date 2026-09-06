# Wealth Logic Transitions, Measured From The Pixels

*Pass-1 · 2026-09-06 · sources: the video on disk, the ledger · for: TR-1*

## The question

What KIND of transition does the Wealth Logic reference use at each of its 99 shot boundaries -
hard cut, dissolve, dip through black, blur-zoom, or a world that persists across the boundary -
and does anything move after the boundary? E38: the threshold comes from the reference, measured
with our own tool, not from a description of the reference.

## Verdict up front

**The reference is not an all-hard-cut edit. Only 36 of its 99 boundaries are hard cuts.**
35 are dips through black - a full fade to L = 0 and back, exactly 14 frames (0.47 s) wide at every
one of them - and 28 are blur-zooms, where the outgoing plate magnifies until its detail collapses,
the frame switches, and the incoming plate resolves over 6-9 frames. 63 of 99 boundaries (63.6 %)
are therefore something other than a cut, and 69 of 99 still have measurable motion half a second
later.
`[DERIVED: from wealth_logic_transitions_measured.csv, count by kind / 99]`

The corollary matters more than the counts: **this channel does not hold a still frame across a
cut.** The one thing the Gemini pass and this pass agree on is that a *hard cut* here is dead
still - boundary 27 measures D = 0.000 for the entire 0.6 s after the switch. But that stillness
covers 36 boundaries, not 99, and it usually does not last: the median hard cut is followed by
7 frames of continuing motion before D settles, and only 17 of the 36 are still under the
"nothing moves" line half a second later.
`[DERIVED: from wealth_logic_transitions_measured.csv, median first_motion_frames where kind=hard-cut]`

### How it was measured, and every threshold in it

`content/video_engine/scripts/measure_cut_kinds.py` decodes `[t - 0.6 s, t + 0.8 s]` around each
boundary at the native **30 fps** (ffprobe: `r_frame_rate=30/1`, 1280x714, AV1, 1013.4 s) as
160x90 grey frames through an ffmpeg raw pipe, and reduces each frame to three series: `L` mean
luminance, `D` mean absolute difference to the previous frame, `S` variance of the Laplacian
(sharpness). No shot in the ledger is shorter than 1.7 s, so no window ever spans two boundaries.
`[DERIVED: from wealth_logic_transitions.csv, min(t_s[n] - t_s[n-1]) = 1.7 s]`

The steady levels (`L_before`, `L_after`, `S_before`) are read from the window EDGES, never from
frames beside the boundary, so a multi-frame transition cannot contaminate its own reference.
The rules fire in this order - most specific mechanism first - and every dial is
**[DERIVED: from the reference video's own series, read off the calibration boundaries below]**,
a starting reference to re-test, never research:

| Rule | Fires when | Dials |
| :--- | :--- | :--- |
| **dip** | `L` leaves the band between both steady levels for >= 3 frames | `DIP_DARK_FRAC 0.60`, `DIP_BRIGHT_FRAC 1.60`, `DIP_MIN_FRAMES 3` |
| **blur-zoom** | `S` falls under half of BOTH steady sharpnesses for >= 2 frames and comes back | `BLUR_VALLEY_FRAC 0.50`, `BLUR_MIN_FRAMES 2` |
| **dissolve** | `D` elevated >= 4 frames, no frame > 3x the run mean, `L` monotone between levels | `DISSOLVE_MIN_FRAMES 4`, `DISSOLVE_DOMINANCE 3.0`, `L_FLAT 3.0` |
| **hard-cut** | `D_peak` > 6x the window median AND the transition spans exactly 1 frame | `HARD_PEAK_RATIO 6.0`, `TRANSITION_FRAC 0.25`, `D_FLOOR 0.4` |
| **world-persists** | `D_peak` < 2x baseline and SSIM(t-0.5, t+0.5) >= 0.60 | `WORLD_PEAK_RATIO 2.0`, `SIM_SAME_WORLD 0.60` |
| **other** | nothing above decides it; the series stay in the csv for a human | - |

Three numbers are reported for every boundary regardless of kind, so "nothing moves after it" is a
number rather than a word: `duration_frames` (the span where `D` or `S` is off-baseline),
`first_motion_frames` (frames after the transition ENDS until `D` settles under `SETTLE_RATIO 1.5`
x baseline) and `motion_after_0_5s` (mean `D` over t+0.1..t+0.6 as a multiple of baseline; 1.0
means the window is as still as the untouched plate).

### Calibration: what the frames show versus what the rules said

Seven boundaries were extracted to `docs/research/runs/wealth-logic-cuts/check/<boundary>/` (grey
analysis frames plus a colour contact strip) and looked at frame by frame. Two were the operator's
spot-checks; five were chosen here. The rules were wrong three times and were fixed each time
against the frames, never the other way round - the fixes are pinned by tests.

| Boundary | What the frames show | First rule said | Now | The fix |
| :--- | :--- | :--- | :--- | :--- |
| 2 (26.2 s) | The character plate switches in one frame into a dark question-mark card that arrives unreadable and resolves over 8 frames (`S` 9090 -> 233 -> 4637). The operator called this a blur-zoom. | `hard-cut` | `blur-zoom` | The valley must be measured against the SOFTER of the two steady levels; the incoming plate is half as sharp as the outgoing one, so a "recovers to 70 % of pre" test could never fire. |
| 4 (35.9 s) | The chain plate fades out to a fully black frame and a new easel plate fades up - both plates visible through the fade, 14 frames, `L` 227 -> 1 -> 233. The operator called this a dip. | `blur-zoom` | `dip` | A black frame has no detail either: the sharpness valley is a CONSEQUENCE of the dip. dip now runs first. |
| 15 (143.2 s) | Vault plate fades to black, a darker stage plate with curtains fades up (`L` 209 -> 0 -> 118). | `dip` | `dip` | - (agreed; the asymmetric levels are a genuinely darker incoming plate) |
| 27 (274.1 s) | Gears plate, one frame, then the "2 / house" plate. Nothing moves at all on either side. | `hard-cut` | `hard-cut` | - (agreed; `D` = 58 on one frame, 0.000 on every other frame in the window) |
| 36 (352.8 s) | The outgoing plate magnifies frame by frame until its detail is gone (`S` 18272 -> 203 over 6 frames), switches, and the incoming plate scales up out of softness. | `blur-zoom` | `blur-zoom` | - (agreed) |
| 98 (997.5 s) | A textbook fade to a fully black frame and up into a two-person plate (`L` 245 -> 0 -> 234). | `other` | `dip` | The dip rule required "the world changed" (SSIM < 0.60); both plates are flat cream figures, SSIM 0.62. The caller already asserts a shot ended, so that guard only ever produced false negatives. |
| 26 (262.5 s) | The boxes plate magnifies over 5 frames, switches, and the two-figure plate scales up out of softness (`S` 2176 -> 306 -> 3073) - the same mechanism as 65. | `hard-cut` | `blur-zoom` | The same guard, on the blur-zoom rule this time: SSIM 0.61 against a 0.60 line. SSIM now decides `world-persists` only, where the `D` peak is too small to say anything on its own. |
| 65 (660.4 s) | Both plates zooming, symmetric valley (`S` 7980 -> 544 -> 8193), the switch itself one frame. | `blur-zoom` | `blur-zoom` | - (agreed; the cleanest picture of what `blur-zoom` names here - a zoom-through, not an optical blur effect) |

Two of the three fixes were the same mistake: a "did the world change" guard, at SSIM 0.60, on a
channel whose plates are all cream backgrounds with one or two figures on them. Boundaries 98
(0.62) and 26 (0.61) sat just above the line while their pixels did something unmistakable. The
caller already asserts that a shot ended at every boundary, so the guard could only ever subtract.

## 1. Hard cut

**36 of 99, 36.4 %** `[DERIVED: from wealth_logic_transitions_measured.csv, count(kind=hard-cut)/99]`
**Median shot length 9.35 s** `[DERIVED: from wealth_logic_transitions_measured.csv, median(t_s[n] - t_s[n-1]) where kind=hard-cut]`

One frame carries the whole change and the frames on either side are steady: the transition spans
exactly 1 frame at every one of the 36. Median `motion_after_0_5s` 1.68, and 17 of the 36 are under
1.5 - genuinely still after the cut.
`[DERIVED: from wealth_logic_transitions_measured.csv, median and count of motion_after_0_5s where kind=hard-cut]`

| # | t_s | duration_frames | first_motion_frames | motion_after_0_5s | D_peak | D_median | L before/min/after | S before/min |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 27 | 274.1 | 1 | 0 | 0.135 | 57.7 | 0.007 | 206.4 / 206.9 / 219.1 | 8666.6 / 5553.8 |
| 61 | 616.4 | 1 | 0 | 0.078 | 92.1 | 0.007 | 215.3 / 168.5 / 168.6 | 5909.8 / 5916.7 |
| 1 | 10.6 | 1 | 7 | 2.268 | 40.3 | 0.023 | 215.2 / 227.5 / 211.4 | 7896.9 / 6605.3 |

Boundary 1 is the instructive one: both plates are animating at `D` ~ 3 and one frame carries
`D` 40.3 - 101x the window median, with the neighbours at 7 % of the peak. Ambient motion does not
hide a cut, and a cut does not imply a still shot.

## 2. Dissolve

**0 of 99, 0.0 %** `[DERIVED: from wealth_logic_transitions_measured.csv, count(kind=dissolve)/99]`

No boundary showed a cross-fade: `D` elevated over 4+ frames with no dominant peak and `L` sliding
monotonically from one steady level to the other. Every gradual transition in this reference goes
through black (section 3) rather than blending one plate into another. Note what this means
mechanically: the two plates are never on screen together. The rule is live and tested on a
synthetic 6-frame ramp; it simply never fired on this video.

## 3. Dip through black

**35 of 99, 35.4 %** `[DERIVED: from wealth_logic_transitions_measured.csv, count(kind=dip)/99]`
**Median shot length 6.9 s** `[DERIVED: from wealth_logic_transitions_measured.csv, median(t_s[n] - t_s[n-1]) where kind=dip]`

The largest single mechanism after the hard cut, and the one the Gemini pass missed entirely. The
shape is consistent to the frame: `L` falls from ~215-245 to **0 or 1** (the highest `L_min` of the
35 is 0.83) and returns, `duration_frames` **14 at all 35** (0.47 s), median `motion_after_0_5s`
43.9 - by far the most motion of any kind, because the fade IS the motion inside that window. `first_motion_frames` is 0 at all 35: once the
fade-up completes the new plate is immediately still.
`[DERIVED: from wealth_logic_transitions_measured.csv, median duration_frames / motion_after_0_5s / first_motion_frames where kind=dip]`

| # | t_s | duration_frames | first_motion_frames | motion_after_0_5s | D_peak | L before/min/after | S before/min |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 4 | 35.9 | 14 | 0 | 18.151 | 33.9 | 226.8 / 0.8 / 233.0 | 7608.7 / 146.2 |
| 98 | 997.5 | 14 | 0 | 52.857 | 36.5 | 244.6 / 0.0 / 234.1 | 1761.8 / 0.0 |
| 15 | 143.2 | 14 | 0 | 17.403 | 31.0 | 209.0 / 0.5 / 118.5 | 4463.4 / 97.3 |

These are dips, not dissolves: the frame reaches literal black between the two plates. They sit on
shorter shots than the cuts (6.9 s against 9.35 s), which is the opposite of the usual assumption
that a slower transition marks a slower passage.

## 4. Blur-zoom (zoom-through)

**28 of 99, 28.3 %** `[DERIVED: from wealth_logic_transitions_measured.csv, count(kind=blur-zoom)/99]`
**Median shot length 9.8 s** `[DERIVED: from wealth_logic_transitions_measured.csv, median(t_s[n] - t_s[n-1]) where kind=blur-zoom]`

The outgoing plate magnifies until its fine detail is gone, the frame switches, and the incoming
plate resolves out of softness. The switch itself is instantaneous at **all 28** - the `D` span is
exactly 1 frame every time, which is why a `D`-only rule reads this whole class as a hard cut. `S` falls below half of BOTH steady levels - to
203-949 from 2175-18271 - for a median of 8 frames (0.27 s, range 6-9). Median
`motion_after_0_5s` 1.59, and 13 of the 28 are under the 1.5 "nothing moves" line: the motion in
this class is the resolve, not the plate.
`[DERIVED: from wealth_logic_transitions_measured.csv, median duration_frames / motion_after_0_5s where kind=blur-zoom]`

| # | t_s | duration_frames | first_motion_frames | motion_after_0_5s | D_peak | S before/min | S after (series) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2 | 26.2 | 8 | 0 | 1.473 | 133.1 | 9090.2 / 233.5 | 4637 |
| 36 | 352.8 | 6 | 1 | 0.756 | 51.3 | 18271.2 / 203.4 | 2076 |
| 65 | 660.4 | 8 | 2 | 2.154 | 67.5 | 8057.6 / 543.8 | 8193 |

Boundary 2 is the one the operator flagged: `D_peak` 133 on a single frame (the highest in the
video), so a rule that looks only at `D` calls it a hard cut - and it *is* an instantaneous swap.
What makes it a blur-zoom is what surrounds the swap: 8 frames where nothing on screen is legible.

## 5. World-persists

**0 of 99, 0.0 %** `[DERIVED: from wealth_logic_transitions_measured.csv, count(kind=world-persists)/99]`

No ledger boundary turned out to be an element entering or leaving a background that stays. Every
one of the 99 replaces the whole frame. This is a real finding about the reference and not a
measurement gap: the rule fires on a synthetic flat-`D` series in the tests. It also means the
ledger's 99 boundaries and the video's 99 plate changes are the same set - the ledger did not
count in-shot events as shots.

## 6. Other

**0 of 99, 0.0 %** `[DERIVED: from wealth_logic_transitions_measured.csv, count(kind=other)/99]`

Every boundary was decided by a rule. One (boundary 98) landed in `other` on the first full pass and
was reclassified after its frames were opened - see the calibration table. In both that case and
boundary 26's, the rule was changed and the row followed; no row was ever edited to a kind its
series did not support.

## 7. What the Gemini pass got wrong

`docs/research/motion/WEALTH_LOGIC_TRANSITIONS_RESEARCH_BLUEPRINT.md` and its
`wealth_logic_transitions.csv` are left untouched; this section marks their row-level claims as
contradicted, by boundary count. The blueprint's verdict is "Every cut in the Wealth Logic
reference is a hard cut... zero wipes, dissolves, or push transitions", and its csv asserts four
things on every one of the 99 rows: `kind=hard-cut`, `duration_frames=0`, `world=changes`,
`first_motion=nothing`.

| Claim (all 99 rows) | Measured | Contradicted at | The number that decides |
| :--- | :--- | :--- | :--- |
| `kind = hard-cut` (99/99) | 36 hard-cut, 35 dip, 28 blur-zoom | **63 of 99** | `L_min` reaches 0-1 at 35 boundaries; `S_min` falls under half of both steady levels at 28 |
| `duration_frames = 0` | 1 frame at every hard cut, 14 at every dip, 6-9 at every blur-zoom | **99 of 99** | `duration_frames` in the measured csv; no transition occupies zero frames |
| `first_motion = nothing` | 69 boundaries have `motion_after_0_5s` >= 1.5 | **69 of 99** | `motion_after_0_5s`, mean `D` over t+0.1..t+0.6 relative to baseline |
| "zero dissolves" (section 2) | 0 cross-fades - but 35 fades through black | agreed on the letter, **contradicted at 35** on the substance | `L` reaches literal 0 and returns over 14 frames |
| Median shot length 9.6 s | 9.4 s over the 99 shots that end at a boundary, 9.55 s including the final shot | not contradicted | but it hides the split: 9.35 s at hard cuts, 6.9 s at dips, 9.8 s at blur-zooms |

Sample rows, Gemini's kind against the measured kind:

| Boundary | t_s | Gemini | Measured | The number that decides |
| :--- | :--- | :--- | :--- | :--- |
| 2 | 26.2 | hard-cut | blur-zoom | `S` 9090 -> 233 for 8 frames, both steady levels >= 4637 |
| 4 | 35.9 | hard-cut | dip | `L` 226.8 -> 0.8 -> 233.0 over 14 frames |
| 15 | 143.2 | hard-cut | dip | `L` 209.0 -> 0.5 -> 118.5 over 14 frames |
| 36 | 352.8 | hard-cut | blur-zoom | `S` 18271 -> 203, recovering to 2076 |
| 65 | 660.4 | hard-cut | blur-zoom | `S` 8058 -> 544 -> 8193 |
| 98 | 997.5 | hard-cut | dip | `L` 244.6 -> 0.0 -> 234.1 over 14 frames |
| 26 | 262.5 | hard-cut | blur-zoom | `S` 2175 -> 306 -> 3073, an 8-frame valley around a 1-frame switch |
| 27 | 274.1 | hard-cut | hard-cut | `D` 57.7 on one frame, 0.000 on every other frame - the claim holds here |

The blueprint's `at_gap` / `gap_s` columns are derived from `video.en.vtt` and are not contradicted;
they are carried through into the measured csv unchanged (71 of 99 boundaries land in a speech gap).

## Sources

- `docs/research/runs/wealth-logic-cuts/wealth-logic-6-ways.mp4` - the reference video on disk
  (1280x714, AV1, 30/1 fps, 1013.4 s, 30403 frames; ffprobe 2026-09-06). Working frames and series:
  `docs/research/runs/wealth-logic-cuts/check/` (gitignored, not indexed).
- `content/video_engine/sources/reference_analyses/complete_research_evidence_bundle/04_shot_ledger_100_cuts.md`
  - the 99 boundary times (End of shot N).
- `docs/research/motion/wealth_logic_transitions.csv` - the Gemini pass's boundary list and its
  `at_gap` / `gap_s` columns (kept), and its `kind` column (contradicted).
- `docs/research/motion/wealth_logic_transitions_measured.csv` - this pass's output, 99 rows.
- `content/video_engine/scripts/measure_cut_kinds.py` + `content/video_engine/tests/test_measure_cut_kinds.py`
  - the tool and the synthetic-series tests that pin each rule.
- `docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md` - the review that asked the question.

## NOT FOUND WHERE I LOOKED

- **Whether the blur-zooms are optical blur or scale-driven detail loss.** Searched: the decoded
  frames themselves at 160 px (analysis) and 240 px (viewing) for boundaries 2, 26, 36, 65, frame by
  frame. `S` cannot separate "the plate was blurred" from "the plate was magnified until its lines
  crossed fewer pixels"; the frames at 240 px show progressive magnification but are too small to
  settle it. A per-frame optical-flow or scale-estimate pass at full resolution would.
- **Whether any dip is a fade to white rather than to black.** The bright-dip rule
  (`DIP_BRIGHT_FRAC 1.60`) ran on all 99 and never fired; with steady levels already at L ~ 215-245
  on this channel's cream plates, a fade to white cannot reach 1.6x and would be invisible to that
  rule. Coverage limit: a white flash on a cream plate would currently read as `other`, and nothing
  read as `other`.
- **Audio at the boundary.** Not searched. The window is video-only; whether a whoosh or a music
  edit accompanies the dips is a separate pass over the audio track.
- **The 100th cut.** The ledger is titled "100 cuts" and lists 100 shots; the boundary list holds
  the 99 internal boundaries (shot 100 ends at the runtime). Nothing was measured at t = 0 or at
  the end of the video.
- **Any other Wealth Logic video.** Only `wealth-logic-6-ways.mp4` is on disk under
  `docs/research/runs/`. Searched: `docs/research/runs/`, `content/video_engine/sources/reference_analyses/`.
  Whether these shares hold across the channel is untested and this report does not claim it.
