# The race read - content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short-t17/arm-b

433 frames at 60 fps over 4.5-11.7 s; 5 racing marks; the geometry axis resampled every 2 px of arclength so the clock is out of it.

| axis | reading | value | what it is |
|---|---|---:|---|
| TIMING | timing energy (px^2/s^5) | 1,374,304,275,197 | `integral (d2|v|/dt2)^2 dt` - zero at any constant speed, whatever the shape |
| TIMING | speed CV | 1.068 | the speed's own spread over the window |
| TIMING | stall fraction | 0.194 | share of frames under 10% of the mean speed |
| TIMING | join speed dip | 0.043 | speed AT a period, over the mean. Near 0 = the mark stops dead at every period |
| GEOMETRY | bending `integral k^2 ds` (1/px) | 8.712265 | how hard the path bends |
| GEOMETRY | fairness `E_MVS = integral (dk/ds)^2 ds` (1/px^3) | 3.22719 | the functional Euler spirals minimise (42 s42.4) |
| GEOMETRY | join curvature PEAK, mean (1/px) | 0.137430 | max |k| at the period knots - a CORNER is a spike |
| GEOMETRY | join curvature peak, max (1/px) | 0.754511 | the worst join |
| GEOMETRY | join curvature STEP, mean (1/px) | 0.028930 | |k after - k before| - what G2 continuity forbids, and what the fitter removes |

## Per mark

| mark | path (px) | mean px/s | timing energy | speed CV | stalls | join dip | bending | fairness | join peak | join step |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ALPHA | 348 | 48 | 301,014,615,185 | 1.027 | 0.222 | 0.038 | 0.391635 | 0.0874914 | 0.145463 | 0.042246 |
| BETA | 303 | 42 | 289,356,554,550 | 1.275 | 0.391 | 0.046 | 0.369815 | 0.0835462 | 0.077664 | 0.027732 |
| CHI | 441 | 61 | 498,445,667,590 | 1.053 | 0.144 | 0.043 | 4.810983 | 1.96355 | 0.404689 | 0.026203 |
| DELTA | 353 | 49 | 250,263,776,835 | 0.830 | 0.079 | 0.042 | 3.139832 | 1.0926 | 0.754511 | 0.425186 |
| EPS | 113 | 16 | 35,223,661,037 | 1.155 | 0.134 | 0.048 | 0.000000 | 0 | 0.000000 | 0.000000 |

Read the two axes against the OTHER ARM, never against a threshold: neither number has a published floor, and the A/B is the whole point.

## What this read does and does not see

- The GEOMETRY axis is measured on the mark's path in SCREEN pixels, which carries the axis glide (the race retargets `scaleMax` every frame as the leader grows). Both arms carry the same glide, so the A/B is fair, but an absolute curvature here is not the curvature of the data-space path a fitter would be fitting.
- A row that never changes rank travels a straight horizontal line whatever the clock does, so its curvature is zero BY CONSTRUCTION. That row is the control: whatever choppiness it has cannot be curvature.
- This is DOM geometry - the bar's tip, not pixels. Blur, colour, stroke width and anything inside a raster are invisible to it.
