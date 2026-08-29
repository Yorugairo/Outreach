# P16 T3 — Martial Editorial Adapter Evidence

Date: 2026-08-07
Status: complete; Gate 1 authorization signature pending

## Outcome

- Added fail-closed schemas for `editorial_review_authorization.v1` and
  `martial_editorial_adapter_manifest.v1`.
- Added a job-contained Martial adapter that verifies the immutable Marshall
  r1 package, 192 cue/plate pairs, selected file hashes, canonical audio,
  1,528-word timing, caption inputs, authored midpoint boundaries, and cue
  event instructions.
- Added an authorization-only explicit clock path. Legacy timestamped
  compilation remains the default when explicit ranges are absent.
- Added `compile-martial-editorial`, plus job-root/revision shorthands for
  validation and rendering.
- Materialized the existing deterministic default pacing recipe as an explicit,
  hash-bound CLI input; no pacing values changed.
- Added optional adapter-manifest and contained-file integrity checks to
  editorial-motion QC.
- The adapter writes only beneath
  `content/video_engine/runtime/jobs/<job>/animatic/revisions/<revision>/`
  and does not change source render flags or catalog state.

## Immutable r1 Inputs Verified

- Edit package artifact: `748fe4afe7f864b859d56d8ab0458bdf6b50460a5ffb2e2857934c50ab3ec9b1`.
- Cue-sheet artifact: `49a46788f24f08083c28465dc6dafffe96e07c5cd1cb130ae2b1d7c4e43b02c3`.
- Canonical audio-manifest artifact: `3a04fe2318b8a01abc3113712fa8e7a86f2d1879b7bf07828af3a2e0a43bef31`.
- Canonical audio content: `b5d8e372217e92529efaafee2493cbcb1c160ba21c6e084802a833d2413fda48`.
- Word timing file: `9bf403c6e9299663d6f29770a0f42d68c4d03c22d96598903973c4d7cfcdc403`.
- Counts and bounds: 192 cues/assets, 1,528 words, contiguous
  `0.000–567.804` seconds.
- All 192 selected PNGs resolved and matched their declared SHA-256 values.
- All 57 cues longer than 3.35 seconds carry at least one authored material
  event.

## Validation

```text
python -m py_compile ...
  pass

python -m pytest \
  content/video_engine/tests/test_martial_editorial_adapter.py \
  content/video_engine/tests/test_editorial_motion.py \
  content/video_engine/tests/test_editorial_motion_qc.py -q
  58 passed in 2.41s

python -m content.video_engine.cli compile-martial-editorial --help
  pass; all required explicit inputs registered

npm --prefix content/video_engine/editor run typecheck
  pass

git diff --check
  pass (line-ending notices only)
```

The full video-engine suite reached 357 passed and 5 failed. All five failures
are the pre-existing `test_history_v4_pipeline.py` checked-in fixture/hash
failures present in the exact P13 base; P16 does not modify those history
assets or manifests.

## Gate State

- Remotion classification: sole-user creator workflow; current free-license
  tier applies under Remotion's published pricing terms.
- Authorization remains intentionally unsigned until the operator explicitly
  approves scope `internal_revision_render_only` for the exact 192 r1 hashes.
- Publication and catalog-promotion authorization remain false.
