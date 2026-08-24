# 37 — TTS Delivery Standards (ElevenLabs)

*Research 2026-08-24 · ElevenLabs official docs (primary source throughout) ·
Confidence: High — every claim verified against elevenlabs.io docs pages.*

The codification the deep-research asked for: are we converting the
writing-for-the-ear doctrine ([32](32-WRITING-FOR-THE-EAR.md)) and the voice
profile ([33](33-VOICE-PROFILE.md)) into what ElevenLabs actually rewards?
Answer: **our doctrine is aligned, our pipeline is under-using the API.** The
audit found five unused capabilities on the exact endpoint we already call.

## 0. Current pipeline state (audited)

`audio_synth.py` calls `/text-to-speech/{voice}/with-timestamps` with
`eleven_multilingual_v2`, `mp3_44100_128`, and a verbatim
`voice_settings` passthrough (observed channel default: stability 0.5,
similarity 0.75). It does **not** send: pause markup, request stitching,
`apply_text_normalization`, `pronunciation_dictionary_locators`, or `seed` —
all of which the endpoint supports
([API ref](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps)).
The repo's pronunciation-dictionary schema exists but nothing attaches
dictionaries to requests.

## 1. Pause marks — the compiler rule

Docs 32/33 mandate `[pre-key]` / `[post-key]` marks in scripts. ElevenLabs'
mechanism is **model-dependent**
([pauses guide](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-can-i-add-pauses)):

| Model | Pause mechanism |
| --- | --- |
| Multilingual v2, Flash v2/v2.5, Turbo | `<break time="1.0s" />` — "the most consistent way"; a natural pause the model understands, not spliced silence. **Max 3 seconds.** |
| Eleven v3 | **No SSML at all.** Audio tags `[pause]`, `[short pause]`, `[long pause]`, plus punctuation and structure. |

**Compilation table (script mark → multilingual v2 payload):**

| Script mark | Compiles to | Rationale |
| --- | --- | --- |
| `[pre-key]` | `<break time="0.6s" />` | the Humes pre-key stop — enough to signal "process what comes next" |
| `[post-key]` | `<break time="1.2s" />` | settle time after the heavy point |
| savor / breathing-room beat > 3s | **nothing in TTS** — assembled as timeline gap in the edit | break tags cap at 3s; long silence belongs to the editor, not the synth |

**Ration rule (official warning):** excessive break tags cause speed-ups and
audio artifacts. Cap **≈3 break tags per generated segment**; micro-pauses
come from punctuation — a dash or em-dash reads as a small pause (our
em-dash-heavy register is already doing this work), `--  --` for slightly
longer. **Ellipses add hesitation/nervousness** — use only when hesitation
is wanted, which in this voice is nearly never.

## 2. Voice settings — codified baseline

Official guidance ([voice settings](https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech),
[best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)):

| Setting | Our standard | Source guidance |
| --- | --- | --- |
| stability | **0.50** baseline; raise to 0.60–0.65 only if chunks drift | narration band 0.4–0.7; "most common setting is stability around 50" |
| similarity_boost | **0.75** | "similarity around 75"; ≥0.75 for branded voices |
| style | **0, always** | official: "we recommend keeping this setting at 0 at all times" — destabilizes, adds artifacts |
| use_speaker_boost | **off** | effect "generally rather subtle," adds latency |
| speed | **1.0** global; 0.9–1.1 is the natural band; per-segment override only, never global tuning | min 0.7 / max 1.2; extremes degrade quality |

Settings are a randomization *range*, not a dial — the API is
non-deterministic. For retakes that must match, pass **`seed`** (supported on
our endpoint).

**Verdict on current config: our 0.5/0.75 is exactly canon.** The codification
adds the style=0 and speed rules so nobody "improves" them later.

## 3. Long-form consistency — request stitching (unused, highest-value gap)

Chunked generation (our per-beat/per-slot model) produces prosody jumps
between chunks. The fix is
[Request Stitching](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching):
pass `previous_request_ids` (up to 3) from the prior segments — the model
maintains prosody across the sequence. `previous_text`/`next_text` are the
weaker text-only variant and are **ignored** when request_ids are present.
Regenerating a middle segment: pass the neighbors as
`previous_request_ids` + `next_request_ids` so the retake splices naturally.

**Standard:** generate slots in order, carry the last ≤3 request ids
forward, persist request ids in the audio manifest so retakes can stitch.
Same model across all stitched segments (official requirement for best
results). Caveat: request stitching requires history — it dies under
zero-retention/`enable_logging=false` modes.

## 4. Numbers — the narration/badge split (doctrine clarification)

The verbatim-figure rule (registration pack, badges) governs **what is
printed on screen**. It must NOT be applied to narration text sent to TTS:
"$93,061" and "3.0 : 1" are typography, not speech.

- **Model policy:** multilingual v2 "does a better job of normalizing
  numbers" ([models doc](https://elevenlabs.io/docs/overview/models)) —
  Flash v2.5 ships with normalization off (enterprise-gated to enable).
  Another reason we stay on multilingual v2.
- **Belt and suspenders:** set `apply_text_normalization: "on"` explicitly
  for narration jobs (modes: auto/on/off; we currently send nothing and
  inherit auto).
- **Writer-side rule (preferred):** critical figures are written out as
  speech in the script — "ninety-three thousand dollars," "three standard
  wafers for every HBM wafer" — per doc 32 §1 (the script is a performance
  document). The badge carries the verbatim typography; the voice carries
  the words. Never let a script line be both.

## 5. Pronunciation — wire the dictionary we already version

The repo schema is model-aware and correct: **phoneme rules** (IPA/CMU) work
on Flash v2 / Turbo v2 (English only); **v3 uses inline IPA natively**;
**multilingual v2 ignores phoneme tags — alias rules only**
([phoneme support](https://elevenlabs.io/docs/help-center/technical/do-pauses-and-ssml-phoneme-tags-work-with-the-api)).

Standard: maintain the dictionary as alias-first (aliases work everywhere),
sync to ElevenLabs, and attach via `pronunciation_dictionary_locators`
(max 3 per request) on every narration job. Finance-name candidates already
observed: tickers ("AVAV" → "A-V-A-V" or "AeroVironment"), "SK hynix,"
"KOSPI," "TSMC."

## 6. Model policy

**`eleven_multilingual_v2` stays the production default** — officially "the
most stable and lifelike... best for narration and post-production," best
number normalization, supports break tags and stitching.

**Eleven v3 is not production-ready for us:** no SSML breaks (whole pause
compiler changes), professional voice clones "not fully optimized" on v3
(official), and expressiveness is not our bottleneck — consistency is.
Revisit when PVC support matures; the compilation table above already
carries the v3 column for that day.

## 7. Implementation gaps (follow-ups, not yet built)

1. Pause-mark compiler: `[pre-key]`/`[post-key]` → break tags at synth time
   (strip from captions/subtitle derivations).
2. Request stitching: thread request ids through `audio_synth.py`, persist
   in the audio manifest.
3. Send `apply_text_normalization: "on"` for narration.
4. Attach pronunciation dictionary locators; add the ticker aliases.
5. Optional: `seed` capture for reproducible retakes.

## Sources

1. [How can I add pauses?](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-can-i-add-pauses) — break tag syntax, 3s cap, artifact warning, punctuation effects
2. [TTS best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices) — v3 pause tags, speed setting, pacing
3. [Voice settings / product guide](https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech) — 50/75 canon, style=0 recommendation, speed bounds, normalization modes
4. [Create speech with timing (API ref)](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps) — our endpoint's parameter support
5. [Request stitching guide](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching) — previous/next_request_ids mechanics
6. [Models](https://elevenlabs.io/docs/overview/models) — normalization by model, model selection
7. [Pauses & phonemes via API](https://elevenlabs.io/docs/help-center/technical/do-pauses-and-ssml-phoneme-tags-work-with-the-api) — per-model phoneme/break support
