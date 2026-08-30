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

**Paragraphs are pause marks (2026-08-29, from the provider docs — the rule
we were missing).** ElevenLabs: *"New paragraphs introduce a clear pause and
reset in intonation."* A blank line in the payload IS a pause mark, as real
as a break tag. The Script F take shipped **37 paragraphs in 8.5k chars** —
the display script's beat-per-paragraph formatting carried into the payload
verbatim — so the voice reset its intonation every one-to-two sentences and
could never build a run. Three rules, enforced by the recorder's preflight:

1. **The payload is REFLOWED, never the display script.** Paragraph breaks
   survive only at true section seams — a register reset the narration
   *wants* (unit exits, the pivot, phase boundaries). Target one paragraph
   per movement, roughly every 45–75s of speech: ≈8–10 paragraphs for a
   six-minute part, not 37.
2. **Never stack pauses.** A break tag adjacent to a paragraph break is a
   double pause (tag + intonation reset) — the "weird gap" class of defect.
   At a kept seam the paragraph break IS the settle: drop the tag. A tag
   survives only mid-paragraph, where an exact duration is needed and no
   reset is wanted.
3. **The full pause inventory is counted together.** Tags, paragraph
   breaks, and em-dashes all pause; the ration rule above governs their
   SUM, not tags alone. 30 em-dashes already carry the micro-pause layer —
   that is the voice, keep it — which is exactly why the tag budget stays
   small.

**The practice target is ≈3 tags PER GENERATION (2026-08-30, after a failed
take).** The provider's own guidance ("How can I add pauses?") warns that
excessive SSML breaks cause speed-ups and artifacts, and its working figure
is about three per generation. §8.3's 12-per-master is a hard CEILING for
pathological cases — reading it as a budget is how yesterday's take went
out with 18 tags and came back with artifacts. Each chained part is one
generation: **target 3 tags per part.** With the payload reflowed, the
movement paragraphs carry the section settles and the em-dash register
carries the micro-pauses; a tag survives only where an EXACT duration is
essential mid-paragraph (the hook settle, an instrument reveal, the tell's
threshold pair, P4's required pre-key, the X5 split seam). Any other
silence belongs to the editor's timeline, where it costs nothing — and it
is OWED, not optional: every settle removed from the payload is recorded
in an **edit-pause plan** (`<script>-EDIT-PAUSES.json`, edit_pauses.v1 —
verbatim anchor, kind, duration, why) that travels with the script. The
recorder's preflight refuses a take without one. The retime pass inserts
the silences at anchor word boundaries and shifts the word timeline; the
roster's savor beats live in the plan, so the duty-roster count includes
it.

**Ration rule (official warning):** excessive break tags cause speed-ups and
audio artifacts. Cap **≈3 break tags per generated segment**; micro-pauses
come from punctuation — a dash or em-dash reads as a small pause (our
em-dash-heavy register is already doing this work), `--  --` for slightly
longer. **Ellipses add hesitation/nervousness** — use only when hesitation
is wanted, which in this voice is nearly never.

## 2. Voice settings — codified baseline

Official guidance ([voice settings](https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech),
[best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)):

**Operator baseline (2026-08-24 — supersedes the generic canon below):**

| Setting | Our standard | Official reference |
| --- | --- | --- |
| stability | **0.40** | narration band 0.4–0.7 — we sit at the expressive end, deliberately |
| similarity_boost | **0.75** | "similarity around 75"; ≥0.75 for branded voices |
| style | **0.20** | official default advice is 0 ("at all times"); operator overrides by ear — watch for the documented instability/artifacts and drop back if they appear |
| use_speaker_boost | **on** | official calls the effect "subtle" with added latency; operator keeps it on |
| speed | **1.0** global; 0.9–1.1 natural band; per-segment override only | min 0.7 / max 1.2; extremes degrade quality |

Two of these (style 0.20, boost on) knowingly diverge from ElevenLabs'
written guidance — recorded as an ear decision under the judge-by-ear rule,
not an oversight. The tripwire: if generations show inconsistent speed,
mispronunciation, or extra sounds, style is the first dial to zero (their
troubleshooting names it specifically).

Settings are a randomization *range*, not a dial — the API is
non-deterministic. For retakes that must match, pass **`seed`** (supported on
our endpoint).

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

## 4b. Non-US currencies — the won problem (observed failure, resolved)

Operator recall checked against the record: the actual observed failure
([22-AUDIO-FIX-RUNBOOK.md](22-AUDIO-FIX-RUNBOOK.md)) was **"5,370 trillion
won" read as the past tense of *win*** — a homograph error, not symbol
mangling. Two research facts frame it:

- ElevenLabs' own sample currency normalizer maps `$ £ € ¥` — **₩ is absent
  from their own example code**. Non-big-four currencies are underserved by
  normalization on every model.
- Official troubleshooting: multilingual models "may mispronounce certain
  words, even in English… especially words that also appear in other
  languages." The homograph class is a known model behaviour.

**Is v3 the fix? No.** v3 shares the English phonetic bias, drops break-tag
support (§1), and its clone quality is officially not optimized. The one
thing v3 adds — native inline IPA — is solvable on v2 by alias. Fix
hierarchy, in order:

1. **Writer-side spell-out** (§4) handles the *symbol*: "₩5,370T" never
   reaches TTS; "five thousand three hundred seventy trillion won" does.
2. **Scoped alias rules** handle the *homograph*: doc 22's designed fix —
   `"trillion won"` → `"trillion wahn"` — scoped to the collocation so it
   can never fire on "he won the race." Extend the same pattern per
   currency-context: "billion won", "million won", "in won". Aliases work
   on every model, including multilingual v2 (phoneme rules do not).
3. **Doc 32 §1 doctrine backstop**: eliminate phonetic ambiguity at the
   writing desk. Where a collision is structural (a currency literally
   named "won"), prefer constructions that disambiguate by context —
   "Korean won" on first mention gives the model its language cue.

Model policy (§6) is unchanged by this finding.

## 5. Pronunciation — wire the dictionary we already version

The repo schema is model-aware and correct: **phoneme rules** (IPA/CMU) work
on Flash v2 / Turbo v2 (English only); **v3 uses inline IPA natively**;
**multilingual v2 ignores phoneme tags — alias rules only**
([phoneme support](https://elevenlabs.io/docs/help-center/technical/do-pauses-and-ssml-phoneme-tags-work-with-the-api)).

Standard: maintain the dictionary as alias-first (aliases work everywhere),
sync to ElevenLabs, and attach via `pronunciation_dictionary_locators`
(max 3 per request) on every narration job. Finance-name candidates already
observed: tickers ("AVAV" → "A-V-A-V" or "AeroVironment"), "SK hynix,"
"KOSPI," "TSMC," and the scoped won aliases from §4b / doc 22.

## 6. Model policy

**`eleven_multilingual_v2` stays the production default** — officially "the
most stable and lifelike... best for narration and post-production," best
number normalization, supports break tags and stitching.

**Eleven v3 is not production-ready for us:** no SSML breaks (whole pause
compiler changes), professional voice clones "not fully optimized" on v3
(official), and expressiveness is not our bottleneck — consistency is.
Revisit when PVC support matures; the compilation table above already
carries the v3 column for that day.

## 7. Implementation status (built 2026-08-24, TDD, 18/18 tests green)

All five gaps closed in `content/video_engine/src/services/audio_synth.py`:

1. **Pause-mark compiler** — `compile_pause_marks` / `strip_pause_markup`:
   `[pre-key]` → 0.6s, `[post-key]` → 1.2s break tags; ration warning above
   3 tags/segment; break-tag tokens never reach the word-timing sidecars
   (alignment reconciles whether the provider echoes or strips the tags);
   cache key uses compiled text so a pause edit re-synthesizes.
2. **Request stitching** — `previous_request_ids` (≤3) chained across scenes
   in storyboard order; provider `request-id` captured from response headers
   and persisted in the words sidecars for retake stitching.
3. **`apply_text_normalization: "on"`** sent by default
   (`ELEVENLABS_TEXT_NORMALIZATION` overrides; validated auto/on/off).
4. **Dictionary attachment** — `pronunciation_dictionary_locators` (≤3
   enforced) from config/env; dictionaries shipped at
   `configs/pronunciation/` — **finance-core** (scoped won aliases per
   §4b/doc 22; tickers by SPOKEN NAME per operator ear-probe 2026-08-24:
   Applied, laze, Ionic, ay-sick, AeroVironment; TSMC/KOSPI/SK hynix) and
   **bjj-core** ("vale tudo" → "valé tudo"; all Japanese/Portuguese names
   verified fine). Probe verdicts: `configs/pronunciation/CANDIDATES.md`.
   Sync via the existing `compile-pronunciation-sync` CLI, then set locators.
5. **`seed`** — config/env (`ELEVENLABS_SEED`), passed when set.

Remaining manual step: run the dictionary sync (operator-gated API write),
then record the returned `dictionary_id`/`version_id` via
`record_sync_result` and set `ELEVENLABS_PRONUNCIATION_DICTIONARIES`.

## Sources

1. [How can I add pauses?](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-can-i-add-pauses) — break tag syntax, 3s cap, artifact warning, punctuation effects
2. [TTS best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices) — v3 pause tags, speed setting, pacing
3. [Voice settings / product guide](https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech) — 50/75 canon, style=0 recommendation, speed bounds, normalization modes
4. [Create speech with timing (API ref)](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps) — our endpoint's parameter support
5. [Request stitching guide](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching) — previous/next_request_ids mechanics
6. [Models](https://elevenlabs.io/docs/overview/models) — normalization by model, model selection
7. [Pauses & phonemes via API](https://elevenlabs.io/docs/help-center/technical/do-pauses-and-ssml-phoneme-tags-work-with-the-api) — per-model phoneme/break support

## §8 — Recording Standards v2 (post-Steel-and-Paper, 2026-08-25)

The first episode's audio failed review: spoken editorial flags, speed-ups
from break-tag overload, and fragments at segment seams. Root cause was
architectural — the episode was synthesized as seven stitched segments and
concatenated, a pattern inherited from the storyboard lane. Provider limits
(verified against ElevenLabs docs, 2026-08-25) make that unnecessary:

| Model | Hard cap per request | ≈ audio |
| --- | --- | --- |
| eleven_multilingual_v2 (ours) | **10,000 chars** | **~10 min** |
| eleven_v3 | 5,000 chars | ~5 min |
| eleven_flash_v2_5 | 40,000 chars | ~40 min (less stable; mv2 is "most stable on long-form") |

Request stitching accepts ≤3 previous_request_ids — it mitigates cross-
request prosody drift; it does not remove seams.

### The MASTER TAKE rule

1. **An episode of ≤ ~9,000 compiled characters records as ONE request**
   (with-timestamps endpoint). Scene boundaries become TIMESTAMPS in the
   words file — cut points in data, never cuts in audio. No concat, no
   seams, one prosody arc, one alignment stream.
2. **Episodes over the cap** split into CHAPTER takes at paragraph ends
   that carry a settle pause, stitched via previous_request_ids, joined
   at detected silence (≥300 ms) with a short crossfade in ONE re-encode
   pass. Never mid-argument, never mid-scene.
3. **Silence belongs to the edit, not the voice.** Break tags are rationed
   (~3 per 1,000 chars, ≤12 per master) and capped at 1.2 s; savor beats,
   breathing dips, and any silence over 1.2 s are timeline gaps between
   words, placed by the editor from the word timings. Overloading breaks
   is the proven cause of provider speed-ups.
4. **Synthesis preflight (mechanical, before any spend):** script lint
   clean · zero bracket flags (the audio layer strips leaks and warns,
   but a warned synthesis is a failed preflight) · numbers written as
   speech · compiled character count vs model cap · break-tag budget
   check · seed pinned · dictionaries attached.
5. **Post-take verification (before the take is accepted):** duration
   sanity (compiled chars / ~14 chars-per-second within ±15%) · alignment
   covers the final word (no clipped tail) · spot-listen the first beat,
   the pivot, and the close · judge-by-ear on the full master before any
   production use. A failed check = seed-locked retake, not repair.
6. **Retakes are per-chapter and seed-locked**; the cache key already
   re-synthesizes on any text change. Repairing a broken take by splicing
   is banned — a seam introduced in repair is the same defect that
   triggered the retake.

Steel and Paper's VO is scheduled for a full master-take re-record under
this standard (single request, ~7k chars) when credits allow; the existing
segmented VO is review-scratch only.

### §8.1 Client timeout and retries — learned the expensive way (2026-08-29)

The first Script C master take **timed out and returned no audio, while
consuming 13,746 characters.** Root cause: the library defaults are sized
for the retired per-scene workflow.

```
DEFAULT_TIMEOUT_S   = 60.0   # a ~1k-char scene renders in seconds
DEFAULT_MAX_ATTEMPTS = 3
```

An 8,078-character master take renders roughly eight minutes of audio and
cannot complete inside 60 seconds. The client abandoned the request
mid-generation and **retried twice — and every attempt is charged.**
8,078 requested, 13,746 spent, nothing delivered.

**Rules for any master take:**

1. **`ELEVENLABS_TIMEOUT_S` must exceed the generation time**, not the
   request round-trip. Budget conservatively at ~20 characters of script
   per second of generation and add headroom — 900s for a ≤10k take.
2. **`ELEVENLABS_MAX_ATTEMPTS = 1`.** On a long paid generation a retry is
   a **cost multiplier, not a safety net**: it will hit the same timeout
   and charge again. Retries are appropriate for short segments and for
   transport errors, never for a timeout on a master take.
3. **Preflight the timeout against the character count** before spending.
   `scratchpad/record_master_take.py` now fails closed on this.
4. **A timeout is not evidence the request was free.** Check the
   subscription endpoint after any failed take — the provider charges on
   generation, not on delivery.

The master-take rule in §8 created this exposure: it replaced many small
requests with one long one, and the retry policy was never revisited to
match. Any doctrine change that alters request *shape* must be checked
against the client's timeout and retry configuration.


## 12. The whisper gate (operator, 2026-08-30)

Provider alignment maps the INTENDED text onto the waveform; it is
structurally blind to the model saying something that was never scripted.
The 0:08 "thumb" (a mangled break tag, vocalized) passed every text gate
because every text gate reads text.

So every recorded take passes a WHISPER GATE before the word timeline is
built: transcribe the audio with a model that has never seen the script
(faster-whisper), normalize both sides, sequence-diff.

- **INSERTED** words (spoken, not scripted) → FAIL. This is the vocalized-
  tag class.
- **DELETED** words (scripted, not spoken) → FAIL. Dropped lines.
- **REPLACED** words are printed but do not fail alone — whisper mishears
  numerals and proper nouns; the human listen adjudicates them.
- WER above 5% → FAIL regardless of class.

Tool: `content/video_engine/scripts/verify_take_whisper.py`. It reads the
recorder's own manifest for audio paths — no path guessing. The gate is a
FILTER before the listen, not a replacement for it: doc §8's "listen to
the join first" stands.

## 13. Probe-first recording (operator, 2026-08-30)

Whisper cannot generate a read - it only transcribes. So "test before
spending" takes this shape: record THE 2:00 PROBE (~2k credits) with the
SAME voice, model, settings and seed as the master, run the whisper gate
and the human listen on it, and only then record the full master.

**Why 2:00 exactly** (operator, 2026-08-30): the first macro section runs
0:00-1:30. A 2:00 sample carries that full section with all its micro
features PLUS the first 30 seconds of the next section - including its
re-hook - so the probe monitors the SHIFT between sections, not just the
section. A probe that ends at the boundary tests a section; a probe that
crosses it tests the video.

Tooling: `record_chained_take.py --probe [--go]` cuts at the first
sentence end past the 2:00 speech estimate and records at master
settings; `verify_take_whisper.py --probe` gates it. Provider artifacts are settings-dependent -
only the provider reproduces its own failure modes, which is why a free
local TTS cannot stand in as the probe. Standing order for every future
master take.


## 14. Kill the dead space, THEN add the breaks (operator, 2026-08-30)

The take comes back carrying dead air the model produced - mid-sentence
holes up to ~2s, slow settles - and stacking our deliberate pauses on
top of it made delivery drag below YouTube pace. Standing order on every
take, enforced by tooling:

1. `compress_dead_space.py` runs on the JOINED take: intra-sentence
   gaps above 0.40s tighten to 0.30s; inter-sentence gaps above 0.65s
   tighten to 0.50s. The six break-tag sites and the join settle are
   AUTHORED silence and are never touched.
2. Only then does `insert_edit_pauses.py` add the owed pauses - it now
   REFUSES to run on an uncompressed timeline.

Deliberate silence is authored; everything else above the caps is dead
air. Script G's raw take measured ~16s of it.

## 15. Name Bravos, not "they" (script gate, 2026-08-30)

The named-subject rule applied to the opponent: any "they/their" whose
referent is Bravos and whose last naming sits more than ~2 sentences
back takes the name. Eight sites fixed in Script G; the sweep is part
of the strength loop's X1 walk for every answer video.


## 16. Stage zero: the scratch take (operator, 2026-08-30)

Before any credit moves, `scratch_take.py` renders the FULL script free,
on two engines with two jobs:

- **Chirp 3 HD** (cloud, ~2 min for a full script, 1M chars/mo free) -
  the LISTEN. The ear pass starts immediately.
- **Kokoro-82M** (local, ~2x realtime, unlimited forever) - the
  EVIDENCE: word timestamps in the take schema, SCRATCH-INDEX.md jump
  points per paragraph, and real chars/sec to replace the rate
  estimators (measured 1.8% off the EL take on the hook vs the
  estimators' ~10% spread).

The scratch tests OUR TEXT - ear failures, pronoun ambiguity, number
reads, pacing shape - and calibrates timing. It CANNOT test ElevenLabs
behavior (tags, seams, appended artifacts, our voice settings): the
2:00 probe (§13) still precedes every master, and scratch timings never
touch the build - the EL take is the only clock.

The ladder: scratch (free, script-level fixes) → 2:00 probe (~2k,
provider + shift) → master (~13k). Each layer catches the failure class
the next layer is too expensive to discover.


## 17. THE AUDIO PATH — canonical, one block (operator-confirmed 2026-08-30)

    script
      -> FULL scratch render      scratch_take.py (Kokoro + Chirp, free)
      -> whisper check + EAR PASS -> fix the script      (repeat until clean)
      -> EL 2:00 PROBE            record_chained_take.py --probe --go (~2k)
      -> whisper check + listen   -> fix if needed
      -> EL MASTER                record_chained_take.py --go (~13k)
      -> whisper gate             verify_take_whisper.py
      -> defended join            join_chained_take.py
      -> word timeline            build_timeline_f.py
      -> KILL DEAD SPACE          compress_dead_space.py --write
      -> add OUR breaks back      insert_edit_pauses.py
      -> retime + TOPIC-EXIT AUDIT + captions -> scene build -> gates

The scratch is full-length (it is free - never sample it); the 2:00 cut
belongs to the PROBE, which tests the provider and the section shift.
Compression precedes the breaks: dead air dies first, deliberate
silence is added back on a tight base.

**Voice watch (operator, 2026-08-30):** on the same text, Chirp 3 HD
Charon read more naturally than our current ElevenLabs voice (whatever
its pronunciation quirks). OPEN QUESTION before the next episode: an
EL settings/voice pass (stability/style sweep, or v3 voices) with the
scratch renders as the comparison bar.


## 18. The half-beat - chart reads breathe at the reveal (operator, 2026-08-30)

Chart-read delivery has a rhythm problem the full-second pause class is
too heavy for: **when the voice names a thing, opens a list, or sets up
a reveal, it needs a HALF-BEAT (0.45s) before the payload** - and after
a threshold statement, a half-beat before the turn.

Three triggers:
- **naming -> list**: "The mega-caps -" [beat] "Meta, Apple, Microsoft..."
- **reveal callout**: "We drew the index underneath them -" [beat]
  "same line."
- **threshold settle**: "...the Fed back above five and a half." [beat]

The selection filter is the CHART: a half-beat is earned where the seam
coincides with a tension reveal on the evidence layer - a delayed
series erupting, a badge landing, an hline drawing. The voice makes the
room; the chart fills it. Ordinary house-style dashes get nothing.

Mechanics: half-beats are EDITOR pauses (kind "half-*" in the edit-pause
plan, applied by insert_edit_pauses.py after the dead-space kill), never
TTS tags - the ~3-tag cap stands. Enumerate candidates by pattern
(colon/dash + payload, threshold sentences), verdict each against the
chart-sync filter, anchor verbatim and UNIQUELY (repeated phrases take
longer anchors).
