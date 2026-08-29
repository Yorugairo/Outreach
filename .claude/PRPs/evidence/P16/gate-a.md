# P16 Gate A — First-Minute Proof

Date: 2026-08-07
Status: awaiting operator watch-through

## Authorization

- Authorization ID: `marshall-monday-001-r1-internal-review-20260807`.
- Authorization artifact:
  `d0e78c315b92bd75fffb25c62aa05666cc7868398280ebd50f4d3cca95dc798c`.
- Scope: `internal_revision_render_only`.
- Exact selected records: 192 cue/path/SHA-256 triples.
- `publication_authorized: false`.
- `catalog_promotion_authorized: false`.
- Operator approval recorded at `2026-08-07T09:00:50.274Z`.

## Compile

- Revision: `gate-a-first-minute`.
- Authored cues: 20.
- Motion-plan duration: 58.833 seconds.
- Motion-plan artifact:
  `a688a3e85fb48123ba6f9b7c0abf9b2f3b0704195e40a5d921e1e04c44d5d14d`.
- Adapter-manifest artifact:
  `1ed8b6ab4afb6b5c20b1ac1e7ebc4ce0225b176ea4080e9fc48bdbbe0f85f887`.
- The first compile failed closed because the final ElevenLabs word ends 1 ms
  after the canonical audio/cue clock. The explicit authorized path now allows
  at most 10 ms of final-word rounding; legacy compilation is unchanged. A
  focused regression proves 1 ms passes and 20 ms fails.

## Structural QC

All checks passed:

- contract integrity;
- asset-map and upstream hashes;
- selected asset resolution and file hashes;
- revision containment;
- adapter manifest and contained-file hashes;
- motion discipline;
- information-surface safety;
- editorial-value discipline;
- zero provider calls.

## Render Evidence

- Profile: 640x360, 15 fps, H.264 video plus AAC audio.
- FFprobe duration: 58.858667 seconds for both files; expected mux rounding
  over the 58.833-second motion plan.
- Normal preview SHA-256:
  `a8a7a511b56dfb93a540f78fc0e73d75eee1ff8896b1460513e804cb0a93c783`.
- Diagnostic preview SHA-256:
  `55c90e87568a36404651368aed2739e45780043d1995f1eb4da04c04301be4e3`.
- Provider calls: 0.
- Cost: USD 0.00.
- Structural quality claim only; human review is required.

Artifacts live beneath:

`content/video_engine/runtime/jobs/marshall-monday-001-p16/animatic/revisions/gate-a-first-minute/`

Gate A approval must cover timing, crop, caption safe band, staging, and motion
behavior. It does not authorize publication, source rights, a full render, or
catalog promotion.
