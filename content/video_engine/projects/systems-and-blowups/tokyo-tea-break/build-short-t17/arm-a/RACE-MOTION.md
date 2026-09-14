# The race read - content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short-t17/arm-a

433 frames at 60 fps over 4.5-11.7 s; 5 racing marks; the geometry axis resampled every 2 px of arclength so the clock is out of it.

| axis | reading | value | what it is |
|---|---|---:|---|
| TIMING | timing energy (px^2/s^5) | 1,511,521,812,895 | `integral (d2|v|/dt2)^2 dt` - zero at any constant speed, whatever the shape |
| TIMING | speed CV | 1.145 | the speed's own spread over the window |
| TIMING | stall fraction | 0.248 | share of frames under 10% of the mean speed |
| TIMING | join speed dip | 0.036 | speed AT a period, over the mean. Near 0 = the mark stops dead at every period |
| GEOMETRY | bending `integral k^2 ds` (1/px) | 5.756875 | how hard the path bends |
| GEOMETRY | fairness `E_MVS = integral (dk/ds)^2 ds` (1/px^3) | 2.73421 | the functional Euler spirals minimise (42 s42.4) |
| GEOMETRY | join curvature PEAK, mean (1/px) | 0.171129 | max |k| at the period knots - a CORNER is a spike |
| GEOMETRY | join curvature peak, max (1/px) | 1.116319 | the worst join |
| GEOMETRY | join curvature STEP, mean (1/px) | 0.012679 | |k after - k before| - what G2 continuity forbids, and what the fitter removes |

## Per mark

| mark | path (px) | mean px/s | timing energy | speed CV | stalls | join dip | bending | fairness | join peak | join step |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ALPHA | 347 | 48 | 322,412,325,779 | 1.103 | 0.248 | 0.033 | 0.476487 | 0.137648 | 0.347270 | 0.036627 |
| BETA | 301 | 42 | 380,488,720,290 | 1.569 | 0.546 | 0.033 | 1.157229 | 0.532056 | 0.494068 | 0.022204 |
| CHI | 427 | 59 | 539,127,667,780 | 1.205 | 0.227 | 0.025 | 1.151413 | 0.40728 | 0.630289 | 0.095916 |
| DELTA | 342 | 48 | 245,868,373,107 | 0.845 | 0.062 | 0.043 | 2.971745 | 1.65722 | 1.116319 | 0.039149 |
| EPS | 96 | 13 | 23,624,725,939 | 1.006 | 0.155 | 0.048 | 0.000000 | 0 | 0.000000 | 0.000000 |

Read the two axes against the OTHER ARM, never against a threshold: neither number has a published floor, and the A/B is the whole point.

## What this read does and does not see

- The GEOMETRY axis is measured on the mark's path in SCREEN pixels, which carries the axis glide (the race retargets `scaleMax` every frame as the leader grows). Both arms carry the same glide, so the A/B is fair, but an absolute curvature here is not the curvature of the data-space path a fitter would be fitting.
- A row that never changes rank travels a straight horizontal line whatever the clock does, so its curvature is zero BY CONSTRUCTION. That row is the control: whatever choppiness it has cannot be curvature.
- This is DOM geometry - the bar's tip, not pixels. Blur, colour, stroke width and anything inside a raster are invisible to it.
