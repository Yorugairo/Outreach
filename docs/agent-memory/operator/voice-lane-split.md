---
name: voice-lane-split
description: Chirp ships on FACEBOOK only - E70 (2026-09-12) superseded E54's YouTube half (no plays, likely mass-produced-voice detection); YouTube voice OPEN; one-shots render both takes; bed -20 LU
metadata: 
  node_type: memory
  type: project
  originSessionId: 59b51626-4ea3-4212-bc22-d97935048fca
  modified: 2026-09-12T18:53:29.384Z
---

Decided 2026-09-01. ElevenLabs is reserved for YouTube masters because of
per-character cost. On the Facebook lane (NotebookLM Video Overview source,
re-voiced), **Chirp 3 HD is the ship voice, not just a scratch take** —
`en-US-Chirp3-HD-Charon` is the operator-approved pick.

**Why:** the Facebook lane's risk is algorithmic clustering with mass-produced
uploads, and the NotebookLM default voice is the strongest cluster signal.
Swapping to any distinct voice addresses that; paying ElevenLabs rates for a
short-form FB cut does not earn its cost.

**How to apply:** this is a deliberate departure from `scratch_take.py`'s
docstring rule ("Scratch timings never touch the build; the EL take is the
clock"), which governs the [production-standards-universal](production-standards-universal.md) YouTube lane.
Don't "correct" a Chirp ship voice on the FB lane back to ElevenLabs. Chirp
`speakingRate` is NOT linear — prefer natural rate plus silence padding over
rate-fitting. See [ear-writing-priorities](ear-writing-priorities.md) for judging the take.

**Amended 2026-09-08 (E54):** the tariff short ships on Chirp on YouTube too — no ElevenLabs spend. The operator learns
the voice from real people watching two cuts side-by-side, with the retention curve as the second witness; the voice is
cheap to change later (every row re-times). The bed rests at −20 LU (+6 on the strip against the old −26 plan) and breathes
+4 dB over each thrown card's landing; it goes no louder — "I don't want too much musical interference."

**Superseded for YouTube 2026-09-12 (E70):** the platform answered — the Chirp cut got basically no plays on YouTube (the
operator suspects Google recognises mass-produced voice) and does fine on Facebook. Facebook keeps Chirp; YouTube's voice
is OPEN and not ElevenLabs by default. A one-shot renders BOTH takes (`scratch_take.py --engine both`). A Chirp clock needs
local alignment (`align_take.py`, faster-whisper), but free ASR dropped 14 of 155 words, so author against a Chirp take only
after forced alignment to the SCRIPT (R26-69). See [local-whisper-no-paid-stt](local-whisper-no-paid-stt.md).
