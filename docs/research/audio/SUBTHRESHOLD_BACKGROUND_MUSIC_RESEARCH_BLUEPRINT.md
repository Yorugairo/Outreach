# Sub-threshold Background Music — Research Blueprint

*Pass-1 discovery brief · 2026-09-01 · sources: Exa semantic + Tavily
extraction · for the Money Physics episode music bed*

## The question

Operator hypothesis: episode music should be "almost as low as
possible; essentially imperceptible," used to (a) fill/mask potential
audio errors and (b) keep the brain subconsciously occupied.

## Verdict up front

**Half right, and the half that's wrong has a better replacement.**

- **The masking/continuity function is real and well-supported** — but
  it requires the bed to be *physically present and just-audible*, not
  imperceptible. This is the room-tone principle, and it matters MORE
  for us than for normal productions because TTS narration has no room
  tone: between phrases our track drops to digital black, and every
  zero-cross butt splice sits on silence. A continuous bed supplies the
  ambience floor that makes edits invisible.
- **The "subconsciously occupied brain" function, at truly
  imperceptible levels, is a myth.** The subliminal-audio literature is
  one of the most decisively negative in psychology: genuinely
  sub-threshold audio produces no reliable behavioral or attentional
  effect. Whatever a bed does, it does by being (barely) heard.
- The correct target is the broadcast criterion: **noticed when absent,
  not when present.** Mute test in reverse.

## Evidence, by sub-question

### 1. Truly imperceptible audio does nothing

- Merikle (1988, *Psychology & Marketing*): commercial "subliminal"
  tapes contain no detectable signal; listeners can't distinguish
  signal from placebo tapes. https://doi.org/10.1002/mar.4220050406
- Egermann et al. (*JASNH* 4(2)): worded messages mixed just below the
  masking threshold of music (SPL-verified) had **zero effect on choice
  behavior** in adults and children.
  https://www.jasnh.com/pdf/Vol4-No2-article1.pdf
- Greenwald et al. 1991 (double-blind, *Psych. Science*): subliminal
  self-help tapes work only via placebo — the belief, not the signal.
- Narrow lab exceptions exist at the detection-without-identification
  boundary — Borgeat 1984 (psychophysiological responses to masked
  words); Signoret et al. 2011, *PLOS One* (semantic priming at
  10 dB-A in slow responders) — but effects are tiny, fragile,
  word-level, and have never scaled to attention, retention, or
  preference. **Nothing here supports an imperceptible music bed doing
  cognitive work for 13 minutes.**

### 2. Audible background music: instrumental ≈ safe, lyrics = speech

- Souza & Barbosa 2023 (*J. of Cognition*, N≈120): lyrics hurt verbal
  memory, visual memory, reading comprehension (d ≈ −0.3);
  **instrumental (lo-fi) had no credible effect either way.**
  https://doi.org/10.5334/joc.273
- Vasilev et al. (4 experiments, self-paced reading): lyrical music =
  as distracting as irrelevant speech when word-rate matched;
  **instrumental music = indistinguishable from silence, sometimes
  slightly FASTER reading.** https://doi.org/10.31234/osf.io/nmdt3
- Brown & Bidelman 2022 (*PMC9562996*): at −5 dB SNR (music nearly as
  loud as speech), full songs mask speech worst; **familiar music
  impairs more than unfamiliar** (listeners "sing along" internally).
- ERP evidence (Sci. Reports 2020): at normal listening levels even
  instrumental music enlarges N400 — semantic integration gets harder.
  Level matters; the studies play music at study-music loudness, tens
  of dB above where a bed sits.
- Gonzalez & Aiello 2019 (via Cog. Research 2025 review): salient music
  helps under-stimulating simple tasks, hurts complex ones. A dense
  analysis episode is the "complex task" case → bed must stay far below
  salience during argument; may rise where the load drops (transitions).

**Design implications:** instrumental only, no lyrics ever; unfamiliar
or purpose-made (never a recognizable track — familiarity is an
active penalty); repetitive, low-complexity, low "sonic energy" during
dense segments.

### 3. The masking/continuity mechanism (the real payoff)

- iZotope (room-tone canon): "The brain is so good at filtering room
  tone that we tend not to even hear it. When room tone suddenly goes
  missing, the brain notices — it becomes clear the performance was
  edited." https://www.izotope.com/community/blog/basics-of-room-tone-audio-editing
- Editors use a continuous ambient bed to camouflage cuts, fill gaps,
  and keep takes continuous (Black Rooster, Beverly Boy production
  guides — same doctrine independently).
- For TTS VO this is doubled: no natural room tone exists, so the music
  bed IS the room tone. It hides splice points, provider artifacts,
  and inter-phrase digital silence — the operator's "fill potential
  errors" goal, achieved at just-audible level via energetic masking +
  the brain's steady-state filtering.

### 4. Where to set the fader (industry numbers)

- General practice: music −18 to −22 dB nominal (WeVideo); **under
  dialogue specifically −30 to −35 dB** (Epidemic Sound); duck 6–10 dB
  when a speaker is present (Tone Production); high-pass/notch the bed
  in the 300 Hz–4 kHz dialogue band.
- Dialogue-anchored loudness is the broadcast norm (Netflix: dialogue
  −27 LKFS ±2). YouTube normalizes full-mix to ≈ −14 LUFS integrated.

## Operational spec for Steel and Paper (and MP default)

1. **VO anchor:** master the mix so integrated loudness lands ≈
   −14 LUFS (YouTube target); VO dominates that reading.
2. **Bed level:** start the music bed at **−26 LU below the VO's
   short-term level** while narration runs (bed alone metering roughly
   −40 LUFS momentary). Range to explore by ear: −22 to −30 LU below.
   This is well under every measured-interference regime in the
   literature (studies find effects at 0 to −5 dB SNR; we sit at
   −22 to −30) while staying above the masking floor so it still
   functions as room tone.
3. **Breathe with the structure:** duck an extra ~4–6 dB during
   number-dense/high-load stretches (the complex-task case); let the
   bed rise toward −18 LU under scene transitions and savor pauses —
   exactly where it covers joins and keeps momentum (the simple-task
   case). Our tempo/pause map already marks these regions.
4. **Selection rules:** instrumental, unfamiliar/purpose-made,
   repetitive structure, minimal energy in 300 Hz–4 kHz (or carve it),
   no strong pulse under dense narration.
4b. **Keep the bed dynamically FLAT** (limit it before the mix):
   YouTube's Stable Volume normalizer (mobile/TV) reacts to peaks in
   the whole mix — a bed with swells can make the algorithm duck the
   VOICE to compensate. Flat + quiet defeats it. Also the reason the
   spec is in LU-below-VO, not dBFS fader positions: peak readings
   depend on crest factor; loudness offsets measure what the ear gets.
   (Cross-checked 2026-09-01 against common creator guidance — VO −6
   to −12 dBFS, music −25 to −35 dBFS under speech, −15/−18 solo,
   −14 LUFS/−1 dBTP mix — same window; our target sits deliberately at
   its quiet edge for dense-analysis content.)
5. **Continuity rule:** the bed must be CONTINUOUS through every VO
   splice region — its whole error-masking value is unbroken
   steady-state. Never start/stop the bed at an edit point; that
   re-creates the room-tone-dropout tell.
6. **Acceptance test (both directions):**
   - Mute the bed mid-episode → the track should feel suddenly drier,
     "studio-dead." If nothing changes, the bed is doing no work — too low.
   - After a full viewing → you should be unable to hum the bed. If you
     can, it's too loud or too melodic.

## Confidence & gaps

- HIGH: subliminal-audio null result; lyrics-are-speech; instrumental
  safety at low SNR; room-tone masking doctrine.
- MEDIUM: exact LU offsets — industry figures are craft consensus, not
  experiments; the −22/−30 LU window is triangulated, tune by ear.
- GAP: no study tests retention effects of beds at −25 LU SNR
  specifically (all research uses far louder music). Our Studio
  retention curves become the experiment.
