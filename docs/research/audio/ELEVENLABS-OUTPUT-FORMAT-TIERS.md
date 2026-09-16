# ElevenLabs TTS `output_format` — values and subscription-tier gates

Date: 2026-09-15 · Role: docs_researcher · Method: ElevenLabs official API
reference, fetched as the docs site's own raw markdown (`<page>.md`) so the
tier sentence is quoted byte-for-byte, not summarised. No API call was made
and no key was used.

Why this file exists: `content/video_engine/src/services/audio_synth.py`
requests `mp3_44100_128` (`DEFAULT_ELEVENLABS_OUTPUT_FORMAT`, line 44) and
nothing in our docs recorded what a move to 192 kbps or PCM costs in plan
terms. This is the record.

## Sources

| # | URL | What it gives |
|---|---|---|
| S1 | https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps | `/v1/text-to-speech/{voice_id}/with-timestamps`: the `output_format` enum, its description (the tier sentences), the response schema |
| S2 | https://elevenlabs.io/docs/api-reference/text-to-speech/convert | `/v1/text-to-speech/{voice_id}`: identical `output_format` description and enum |
| S3 | https://elevenlabs.io/docs/capabilities/text-to-speech | "Supported output formats" — rates/bitrates per codec, plus a general paid-tier sentence |
| S4 | https://elevenlabs.io/pricing/api | Checked for a per-plan format matrix. **It does not contain one** (see "Not documented"). |

## The verbatim tier sentences (S1, S2 — identical text on both pages)

Full `output_format` parameter description, quoted verbatim:

> `output_format` (enum, optional, default: mp3_44100_128) — Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM and WAV formats with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.

The two tier gates, isolated:

> MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above.

> PCM and WAV formats with 44.1kHz sample rate requires you to be subscribed to Pro tier or above.

And the only other tier statement anywhere in the TTS capability docs (S3, "Supported output formats"):

> Higher quality audio options are only available on paid tiers - see our [pricing page](https://elevenlabs.io/pricing/api) for details.

## The three formats in question

| enum | rate / bitrate | documented tier gate | source |
|---|---|---|---|
| `mp3_44100_128` | 44.1 kHz MP3 @ 128 kbps (the API default: "default: mp3_44100_128") | **No tier gate stated.** The description gates only 192 kbps MP3 and 44.1 kHz PCM/WAV; 128 kbps falls outside both sentences. S3's "Higher quality audio options are only available on paid tiers" is general and names no format. | S1, S2, S3 |
| `mp3_44100_192` | 44.1 kHz MP3 @ 192 kbps | **Creator tier or above** — "MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above." | S1, S2 |
| `pcm_44100` | 44.1 kHz PCM, 16-bit signed little-endian ("PCM (S16LE)" … "16-bit depth", S3) | **Pro tier or above** — "PCM and WAV formats with 44.1kHz sample rate requires you to be subscribed to Pro tier or above." | S1, S2 |

## Every `pcm_*` value, with gates

Enum values verbatim from the "Allowed values" list on S1/S2.

| enum | sample rate | documented tier gate | source |
|---|---|---|---|
| `pcm_8000` | 8 kHz | **Not documented.** Outside the 44.1 kHz sentence; no other sentence names it. | S1, S2 |
| `pcm_16000` | 16 kHz | **Not documented.** Same. | S1, S2 |
| `pcm_22050` | 22.05 kHz | **Not documented.** Same. | S1, S2 |
| `pcm_24000` | 24 kHz | **Not documented.** Same. | S1, S2 |
| `pcm_32000` | 32 kHz | **Not documented.** Same. | S1, S2 |
| `pcm_44100` | 44.1 kHz | **Pro tier or above** (quote above). | S1, S2 |
| `pcm_48000` | 48 kHz | **Not documented.** The gate sentence says "44.1kHz sample rate" only; it does not say "44.1kHz and above". Whether 48 kHz inherits the Pro gate is **not stated** — do not assume it does. | S1, S2 |

`wav_44100` carries the *same* Pro gate as `pcm_44100` (one sentence covers
both) and is the headered equivalent if raw S16LE is inconvenient. The rest of
the `wav_*` ladder (`wav_8000` … `wav_32000`, `wav_48000`) has no documented
gate, with the same 48 kHz caveat.

## Full enum, verbatim (S1 and S2, identical)

`alaw_8000`, `mp3_22050_32`, `mp3_24000_48`, `mp3_44100_128`, `mp3_44100_192`,
`mp3_44100_32`, `mp3_44100_64`, `mp3_44100_96`, `opus_48000_128`,
`opus_48000_192`, `opus_48000_32`, `opus_48000_64`, `opus_48000_96`,
`pcm_16000`, `pcm_22050`, `pcm_24000`, `pcm_32000`, `pcm_44100`, `pcm_48000`,
`pcm_8000`, `ulaw_8000`, `wav_16000`, `wav_22050`, `wav_24000`, `wav_32000`,
`wav_44100`, `wav_48000`, `wav_8000`

MP3 rungs with no documented gate: `mp3_22050_32`, `mp3_24000_48`,
`mp3_44100_32`, `mp3_44100_64`, `mp3_44100_96`, `mp3_44100_128`.
Opus rungs: no gate documented at any bitrate, including `opus_48000_192`
(the 192 kbps sentence says "MP3 with 192kbps bitrate", not Opus).

## Alignment under PCM — the blocker question

The `with-timestamps` response schema (S1), verbatim:

> - `audio_base64` (string, required) — Base64 encoded audio data
> - `alignment` (object, optional, nullable) — Timestamp information for each character in the original text
>   - `characters` (list of string, required)
>   - `character_start_times_seconds` (list of double, required)
>   - `character_end_times_seconds` (list of double, required)
> - `normalized_alignment` (object, optional, nullable) — Timestamp information for each character in the normalized text
>   - `characters` (list of string, required)
>   - `character_start_times_seconds` (list of double, required)
>   - `character_end_times_seconds` (list of double, required)

And the endpoint summary:

> Generate speech from text with precise character-level timing information for audio-text synchronization.

**Documented answer: the schema is stated once, with no dependence on
`output_format`.** There is no sentence anywhere on S1 tying `alignment` or
`normalized_alignment` to a codec, and there is no PCM-specific note. The
alignment is character-level (not word-level) for every format; word timings
are ours to derive, as they already are for mp3.

**What is NOT documented, and must not be inferred:** the docs nowhere state
"PCM returns the same alignment as mp3". The absence of a stated difference is
not a stated guarantee, and both alignment objects are declared `optional,
nullable` in the schema regardless of format. If the record depends on
character timings, **verify empirically on one short PCM request before
committing a take** — a single call comparing the `alignment` payload of
`mp3_44100_128` and `pcm_44100` for the same text settles it; the docs cannot.

## Not documented / unknown

| Question | Status |
|---|---|
| Tier gate for `mp3_44100_128` | **Not documented.** No sentence names it. That it is the API default and falls outside both gate sentences suggests it is ungated, but the docs never say "all tiers" — this is inference, not documentation. |
| Tier gate for `pcm_48000` / `wav_48000` | **Not documented.** The gate names 44.1 kHz only. |
| Tier gate for any `pcm_*` below 44.1 kHz, any Opus, `ulaw_8000`, `alaw_8000` | **Not documented.** |
| A per-plan format matrix on the pricing page | **Not present.** https://elevenlabs.io/pricing/api (S4) carries no format-by-tier table; its only format figure ("44.1kHz, 128-192kbps audio") describes the Music product, not TTS `output_format`. The API reference parameter description is the only per-format tier statement found. |
| Whether `alignment` is identical under PCM vs mp3 | **Not documented either way** (see above). Requires an empirical check. |
| Which plan our account is on | Out of scope for the docs; determines whether `mp3_44100_192` (Creator+) or `pcm_44100` (Pro+) is reachable at all. |

## Consequence for us

Moving the next record to `pcm_44100` requires **Pro tier or above**; moving to
`mp3_44100_192` requires **Creator tier or above**. Today's `mp3_44100_128`
sits below both gates. Confirm the account's plan before the record, and verify
the alignment payload on PCM with one probe request rather than assuming parity.
