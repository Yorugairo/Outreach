---
id: P13-HIGGSFIELD-AUDIO-DRIVEN-LANE
title: P13 Higgsfield Audio-Driven Explainer Lane
status: review
operation: feature
risk: external-provider
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-07-31
updated: 2026-08-01
---

# P13 Higgsfield Audio-Driven Explainer Lane

## Summary

Use the approved Episode 1 storyboard narration as the sole ElevenLabs source,
measure it, cut it into provider windows, and pass only approved plates plus
audio references to Higgsfield. Preserve the old overlapping handoff as
rejected evidence and keep every provider output quarantined until human review.

## Intent And Acceptance

- No visual coverage excerpt is ever spoken as narration.
- Canonical narration, word timings, audio windows, blocks, and hashes validate.
- The bounded proof completes with the attached plate and audio reference.
- No provider output becomes render-eligible automatically.

## Scope

The History Episode 1 job only: narration source, ElevenLabs audio resolution,
audio-aligned Higgsfield blocks, one proof task, and local evidence.

## Not Building

No remaining-block Higgsfield batch, publication, registry write, final Gate-A
approval, commit, push, or replacement of the existing storyboard assets.

## Human Gates

The operator must review the canonical narration and completed proof before any
remaining Higgsfield blocks are submitted. Gate A and Gate B remain unchanged.

## Mandatory Reads

- `docs/content-video-engine/14-HIGGSFIELD-AUDIO-DRIVEN-LANE.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `content/video_engine/src/services/history_narration.py`
- `content/video_engine/src/services/higgsfield_explainer.py`

## Execution Path

```text
storyboard scene narration → history_narration.v1 → canonical ElevenLabs take
→ measured word windows → audio-aligned visual blocks → Higgsfield proof
→ human review → bounded waves → local Remotion assembly → Gate A
```

## Patterns To Mirror

- Content-addressed local artifacts and fail-closed validators.
- `AudioSynthService` `/with-timestamps` boundary.
- Existing quarantined Higgsfield job and task-ID duplicate prevention.

## Task Slices

### T1: Reject overlapping V1 handoff
- Status: completed
- Owner: parent
- Depends on: none
- Write set: `.context/p13-history-v4-1/jobs/.../higgsfield-audio-lane/REJECTED-OVERLAPPING-NARRATION.md`
- Acceptance: prior audio remains immutable evidence and is not render eligible.
- Validate: inspect rejection note and old manifest.
- Evidence: rejection note created.

### T2: Canonical narration and audio
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/src/services/history_narration.py`, `configs/history_narration.schema.json`, `configs/elevenlabs_canonical_audio.schema.json`
- Acceptance: one canonical narration hash, one continuous local master, measured word timings.
- Validate: focused narration tests and CLI validators.
- Evidence: `narration-v2.json`, `canonical-audio-v2.json`.

### T3: Audio-aligned blocks and job manifest
- Status: completed
- Owner: parent
- Depends on: T2
- Write set: `content/video_engine/src/services/higgsfield_explainer.py`, `content/video_engine/cli.py`
- Acceptance: measured audio duration determines block count; all 138 visual slots remain covered.
- Validate: block and job validators.
- Evidence: `blocks-v2.json`, `elevenlabs-manifest-v2.json`, `job-v2-proof-complete.json`.

### T4: Bounded Higgsfield proof
- Status: completed
- Owner: parent
- Depends on: T3 and user authorization
- Write set: job-local provider quarantine only.
- Acceptance: one Seedance proof completes with audio replacement disabled.
- Validate: provider result status, local hash, ffprobe duration.
- Evidence: `provider/higgsfield-v2-proof/block-001.mp4`.

### T5: Human review and remaining waves
- Status: pending
- Owner: parent
- Depends on: T4 and operator review
- Write set: provider quarantine and local manifests only.
- Acceptance: operator approves proof, then bounded waves are explicitly authorized.
- Validate: no duplicate running task IDs; every output remains quarantined.
- Evidence: pending human review.

## Evidence And Handoff

Exact artifact hashes and test verdicts are recorded below. The job is ready for
human proof review and is not complete for publication or Gate A.

## Status

The original V1 block/audio handoff is rejected and preserved as evidence.
The corrected V2 handoff is ready for provider review: the approved storyboard
has a canonical 1,420-word narration, one ElevenLabs master take measuring
559.922 seconds, 56 measured audio windows, and one bounded Seedance proof is
submitted. The remaining blocks are not submitted.

## Completed slices

- Added `higgsfield_audio_blocks.v1` compiler and validator.
- Compiled the active 138 editorial slots into exactly 60 contiguous blocks,
  retaining the 607.998987-second source timeline and the 71-plate batch.
- Added `elevenlabs_block_audio.v1` resolution/synthesis boundary. No matching
  Episode 1 audio exists yet, so the local manifest is intentionally
  `awaiting_audio`; older Armbar/visual-v2 MP3s are not eligible.
- Added Seedance-preferred/Wan-fallback capability preflight, provider job
  manifest, local reference validation, task-ID duplicate prevention, and
  `generate_audio: false` enforcement.
- Added CLI commands and versioned JSON schemas.
- Added `history_narration.v1` and `elevenlabs_canonical_audio.v1` so scene
  narration is separate from visual cues.
- Added audio-aligned block compilation and canonical-audio binding; the
  measured audio duration determines block count and visual coverage is scaled
  once onto that timeline.
- Added a single-take ElevenLabs boundary that chunks only at word boundaries
  when request size requires it, then concatenates and slices locally.

## Evidence

- Blocks: `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/higgsfield-audio-lane/blocks.json`
  - artifact hash `e6defb712efcc1ca03d382bfde6f7fff947ff2a84092435910ac055ca58af6ea`
- ElevenLabs resolution: `.../higgsfield-audio-lane/elevenlabs-manifest.json`
  - artifact hash `38bc2a49be6e16aad50a78e6923ada5ae640f4e7e800d24e15658a1ce9833eb5`
  - status `ready`, 60 timestamped block artifacts, ElevenLabs cost estimate `$1.3466`
- Higgsfield job dry-run: `.../higgsfield-audio-lane/job.json`
  - artifact hash `01d6b4fa4a7ca7be276898c3b8919a8d93e381f0407d3ca603f3d18df843ee40`
  - status `planned`, model `seedance_2_0`, blocks `60`
- ElevenLabs block duration evidence: 60 timestamped items, total narration
  duration `396.788s` (the source coverage timeline is `607.998987s`).
- Rejected V1 evidence: `higgsfield-audio-lane/REJECTED-OVERLAPPING-NARRATION.md`.
- Corrected narration: `.../narration-v2.json`
  - artifact hash `65516c9d9af82bce721ef63f0ab92a594f3bb27b7be3fe3b6fa04b39465cc7c6`
  - 1,420 words, narration hash `4e9b08cea4233871ee554b5a8df254b5d2fb0f298bb3566e2bab66548b1ffb91`
- Corrected canonical audio: `.../higgsfield-audio-lane/canonical-audio-v2.json`
  - artifact hash `5e35c5b027c695babe072cb645021dbec0f9d9bda7bb82259fc37f63f016685e`
  - ready, `559.922s`, 56 audio windows, ElevenLabs cost `$1.0306`
- Corrected blocks: `.../higgsfield-audio-lane/blocks-v2.json`
  - artifact hash `9501614e97eaae39d0eb1cb1dc21f7ecede08d2d2e9d99be50af9ad5319b3fc2`
  - 56 blocks, all 138 coverage slots, timeline `559.922s`
- Corrected block-audio manifest: `.../higgsfield-audio-lane/elevenlabs-manifest-v2.json`
  - artifact hash `9669ca80f71edaf949ec62e999b725639695eb711b519608048f8de4dbc3c636`
- Corrected Higgsfield job: `.../higgsfield-audio-lane/job-v2-proof-complete.json`
  - artifact hash `5d746d4b0440d70e2db6635297002b6dd1f0858951523e9cf9212ee42de3b637`
  - 56 planned items; block 1 task `d2d28244-94eb-4e61-9314-413d25b9db79` complete
- Proof output: `.../provider/higgsfield-v2-proof/block-001.mp4`
  - Seedance 2.0 completed, measured duration `10.041667s`
  - SHA-256 `baf461fab9878d8ac26bdab7b0c1dea943979a932e017cb049360d0f7bb190ec`
  - ffprobe reports a video-only H.264 stream; provider audio is absent.
  - quarantined job manifest: `.../higgsfield-audio-lane/job-v2-proof-complete.json`
- Higgsfield proof balance: `1,210` credits on Plus; estimated `45` credits.
  Only block 1 was submitted.
- Higgsfield MCP preflight: Seedance 2.0 confirms audio-reference inputs and
  4–15s duration; `generate_audio=false` was accepted. The proof completed.
- Local block-asset assembly: `.../assembly/history-of-bjj-episode-1-block-assets-with-audio.mp4`
  uses all 56 `blocks-v2.json` plate paths plus canonical ElevenLabs audio. The
  earlier `animatic/motion-preview.mp4` assembly is preserved under
  `assembly/superseded/` and is not an active input.

## Verification

- Focused lane tests: `11 passed`.
- CLI V1 dry-run block compilation: valid, 60 blocks / 138 coverage slots.
- CLI V2 narration/audio/block validation: valid, 1,420 words, 559.922s,
  56 blocks / 138 coverage slots.
- CLI job compilation: valid, quarantined and non-renderable; one proof output
  is complete and remains non-renderable.
- Video-engine tests: `266 passed, 1 warning`.
- Remotion `npm run typecheck`: passed.
- Remotion `npm run build`: passed.
- Full repository suite: `698 passed, 1 warning`.

## Human-controlled next steps

1. Review the corrected canonical narration/audio and the single proof. The
   episode now has a measured `559.922s` runtime rather than a padded ten-minute
   visual timeline.
2. Review the completed proof for plate preservation, smooth motion, and
   narration alignment.
3. If the proof passes, obtain/confirm bounded remaining-wave authorization and
   submit blocks in resumable waves. Do not reuse a running task ID or promote
   output automatically.
4. After wave review, assemble
   locally with ElevenLabs audio in Remotion and stop at Gate A.

No publication, registry write, commit, or push is included in this
implementation slice. One bounded provider proof was explicitly authorized and
completed; remaining provider tasks still require the human review checkpoint.

The Higgsfield CLI is installed (`1.1.20`) but remains unauthenticated; the
bounded proof used the authenticated Higgsfield MCP workspace. CLI login is
still optional for future operator-driven waves.
