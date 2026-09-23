# S13 Blender mechanism proof

Status: **review-only diagnostic**; `render_eligible=false`; no operator or HG2 approval claimed.

## Scope

This is a five-second, 24 fps, 2560x1440 schematic cutaway for S13. It uses rigid, code-authored geometry: an abstract RRP adjustment chamber approaches a marked low stop while two alternative route rails remain visibly open and unassigned. The amber span is an illustrative geometric cue, not a financial quantity, source observation, chart, or prediction. There is no fluid simulation, generated text, label, or source-data import. Labels are intentionally reserved for the later code composition.

Camera: orthographic, 35° azimuth / 25° elevation after one 8° reveal over frames 1–36; locked from frame 37. All animated poses use direct keyframes with linear interpolation and no physics/simulation.

## Files and validation

Builder mode: `samples`. Samples: frames 1, 36, 60, 120. Reverse-seek equality: **True** (see `determinism.json`).

Diagnostic still candidates for parent comparison (not production outputs): `frames/candidate-a-current-120.png`, `frames/candidate-b-no-hatch-120.png`, and `frames/candidate-c-pulledback-120.png`. The optional movie is intentionally withheld pending visual comparison; the 2D route remains the default.

The full movie, when present, must be checked independently with the exact ffprobe command recorded below. A CLI probe is not a render test or asset approval.

```text
C:/Program Files/Blender Foundation/Blender 5.2/blender.exe --background --factory-startup --python build_mechanism.py -- --samples
C:/Program Files/Blender Foundation/Blender 5.2/blender.exe --background --factory-startup --python build_mechanism.py -- --render
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration -of json proof.mp4
```

## Custody

All files are code-authored review outputs. `quarantine-manifest.json` is the custody record; the operator must inspect representative frames and compare the 2D fallback before any promotion. This proof does not alter the episode builder or shared renderer.
