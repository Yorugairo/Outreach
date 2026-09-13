---
name: local-whisper-no-paid-stt
description: "Whisper runs locally — never pay for speech-to-text (ElevenLabs Scribe, cloud STT APIs)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 59b51626-4ea3-4212-bc22-d97935048fca
  modified: 2026-09-02T05:37:40.672Z
---

Whisper is available locally on this machine. Do NOT call paid STT APIs
(ElevenLabs Scribe, Google STT, OpenAI Whisper API) for transcription or word
timestamps.

**Why:** operator called this out on 2026-09-01 after I ran ElevenLabs Scribe
on a 72s clip without asking — the spend was trivial but entirely avoidable,
and the local path was already there.

**How to apply:** reach for local Whisper for any transcript or word-timing
need. Kokoro-82M (installed, `am_michael`) also emits word timestamps at zero
cost when the audio is being *generated* rather than transcribed — see
`scratch_take.py`. Paid audio spend is fine where there's no local equivalent
(ElevenLabs TTS and speech-to-speech), but confirm before spending. Relates to
[voice-lane-split](voice-lane-split.md).
