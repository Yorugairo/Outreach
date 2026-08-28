# P13 Higgsfield Audio-Driven Explainer Lane

> **STATUS: RECORD.** A point-in-time research note, review, or planning document. Not maintained, and not current doctrine — read it for how a decision was reached, not for what to do now. Live doctrine is indexed in [README.md](README.md).

## Narration ownership correction

The first implementation exposed a timing bug: it partitioned the visual
coverage timeline into sixty ten-second groups and sent each group's
overlapping `narration_excerpt` to ElevenLabs. Those excerpts are editorial
cues, not script. The resulting MP3s are preserved as rejected evidence and
must never enter Higgsfield or Remotion.

The corrected lane is:

```text
approved storyboard scene narration
→ history_narration.v1
→ one continuous ElevenLabs take (large word-boundary chunks only when the provider limit requires it)
→ measured word timings
→ ten-second audio windows
→ visual coverage scaled onto the measured audio timeline
→ Higgsfield proof / local Remotion assembly
```

`history_narration.v1` is the canonical script contract. `visual_beats[].narration_excerpt`
is cue text only and is prohibited as TTS input. The provider may receive a
few word-boundary chunks for request-size limits, but the local master is
concatenated before slicing and remains the sole narration source.

This specification records the provider boundary for the History Episode 1
motion experiment. It is additive to the V4/V4.1 pipeline and does not alter
legacy technique, Armbar, or deterministic documentary jobs.

## Local-first contract

The current Episode 1 coverage contains 138 reviewed editorial slots and the
generated-image batch contains 71 hash-bound plates. The lane compiles those
inputs into exactly 60 contiguous blocks. Each block requests a ten-second
provider clip but retains its exact source duration (the current coverage
totals 607.998987 seconds); if the source beat is not exactly ten seconds,
only the silent video is time-fitted locally. ElevenLabs narration is never
trimmed.

The block compiler preserves source beat IDs, narration excerpts, claim and
citation references, the best overlapping plate, recurring cast references,
micro-events, and one motion action. Its output is
`higgsfield_audio_blocks.v1` and remains `render_eligible: false`.

## Audio identity and rights boundary

Episode audio is selected only through
`elevenlabs_block_audio.v1`. A ready manifest must match the block-plan hash,
storyboard hash, narration hash, voice ID, local audio SHA-256, duration, and
word timings. Audio from an Armbar or visual-v2 job is rejected even when the
file is present locally. When no matching artifact exists, the lane returns
`awaiting_audio`; synthesis is opt-in through the existing `AudioSynthService`
and its `/with-timestamps` endpoint, one block at a time.

The ElevenLabs voice ID is operator configuration (`ELEVENLABS_VOICE_ID` in
the worktree `.env` or `docs/local.env`), never a checked-in value. ElevenLabs
remains the canonical narration and any provider-generated sound is discarded.

## Provider preflight and task ledger

`seedance_2_0` is preferred only when a live capability snapshot confirms
ten-second audio-reference support. `wan2_6` is the explicit fallback. Both
paths require a visual reference, permit a bounded audio-reference list, and
set `generate_audio: false`. With no live snapshot, preflight may compile a
dry-run but marks `requires_operator_live_preflight: true`.

The provider job is `higgsfield_audio_job.v1`. Every item includes its plate,
approved character references, local ElevenLabs audio hash, one-action prompt,
negative prompt, task ID, retry state, and `render_eligible: false`. A running
task ID cannot be silently replaced or duplicated. Higgsfield output remains a
quarantined candidate until human review and promotion; Remotion remains the
authoritative assembly layer for captions, citations, credits, narration, and
vertical reframes.

After every provider item has a reviewed local output, the
`higgsfield_local_assembly.v1` contract binds those clips to the ready
ElevenLabs manifest. It is the only handoff consumed by Remotion; provider
audio is explicitly discarded and the artifact remains non-renderable until
the normal gates.

## Dry-run commands

```powershell
python content/video_engine/cli.py compile-higgsfield-blocks `
  --coverage <job>/editorial_coverage.json `
  --generated-batch <job>/generated_blocks/batch.json `
  --job-dir <job> `
  --output <job>/higgsfield-audio-lane/blocks.json

python content/video_engine/cli.py resolve-elevenlabs-audio `
  --blocks <job>/higgsfield-audio-lane/blocks.json `
  --job-dir <job> `
  --output <job>/higgsfield-audio-lane/elevenlabs-manifest.json

python content/video_engine/cli.py compile-higgsfield-job `
  --blocks <job>/higgsfield-audio-lane/blocks.json `
  --audio <job>/higgsfield-audio-lane/elevenlabs-manifest.json `
  --job-dir <job> `
  --output <job>/higgsfield-audio-lane/job.json
```

No command above submits a provider task. A live capability check and a
separate bounded Higgsfield authorization are required before any generation.
