# The gaps and the edit — measured, then corrected, 2026-09-04

Operator brought back an observation from a video on AI-generated content: the makers
record audio, transcribe to a word timeline, and **use the gaps to dictate scene
generation** — instead of compressing the gaps and re-timing a visual plan onto the
shortened clock.

I measured it on our own material, twice. **The first result looked like a clean
confirmation and was an artifact. The second contradicts it.** Both are below, because
the second is the one that generalises and the first is the trap.

---

## Test 1 — the 90-second short (Kokoro TTS). Looked perfect. Isn't.

`SCRIPT-90S-VO.txt`, 327 words, 117.8 s, cut wherever a gap exceeds 0.30 s:

| | |
|---|---|
| gap-driven scenes | **13** |
| hand-authored shots in `SHOT-TABLE-90S.md` | **13** |
| scenes passing M01 (≤12 s) by construction | 11 of 13 |
| silence | 14.5 s = 12% of runtime |

Every gap ≥0.30 s was also ≥0.70 s — apparently bimodal, no threshold to tune.

**It was circular, and the circularity was the whole result.** Kokoro pauses at
paragraph breaks and almost nowhere else — 12 gaps in 327 words. I had authored one
shot per paragraph. So gaps = paragraphs = my shots, by construction. This measured
the TTS engine's punctuation handling, not anything about editing.

## Test 2 — the real ElevenLabs take. The finding does not survive.

Steel and Paper, 2,457 words, 806 s, 75 hand-authored scenes. Gap-driven cuts against
the authored scene starts (±0.75 s tolerance):

| threshold | cuts | scene starts matched | recall | precision |
|---|---|---|---|---|
| 0.20 s | 180 | 33 / 75 | **44%** | 18% |
| 0.30 s | 110 | 21 / 75 | 28% | 19% |
| 0.50 s | 62 | 10 / 75 | 13% | 16% |

**The gaps do not predict where we cut.** Best case is 44% recall at 18% precision,
which is close to chance for this cut density.

And the raw take (pre-tempo-edit, pre-inserted-pause) shows why the short misled me:

| | short (Kokoro) | real take (ElevenLabs) |
|---|---|---|
| silence | 12% | **24%** |
| gaps | 12 | 2,879 |
| median gap | 1.269 s | **0.058 s** |
| distribution | bimodal | **continuous, long tail** |

A real take has a micro-gap between almost every word. There is no natural cut list in
it. There *is* a real inflection around 0.30–0.40 s (111 gaps → 41), but that is a
choice of threshold, not a property of the audio.

## What actually holds

**1. We cut more often than the narrator pauses, and not at the pauses.** 75 scenes in
806 s is one every 10.7 s; gaps ≥0.30 s arrive every 7.3 s. There were more pause
opportunities than we used, and we mostly did not take them. Whether that is a defect
or a deliberate momentum choice is a real question — cutting mid-sentence pulls
forward, cutting on a breath settles — but it is currently **unexamined**, and the
operator's video suggests one of those two is being left on the table.

**2. Compressing the gaps is a bad trade, and this survives both tests.** On the short:
117.8 s → 103.3 s. The target is 90 s. It **does not solve the length problem**, and it
costs whatever scene signal the gaps carried, and it forces the entire `retime_to_take`
machinery that exists only because the clock moved. That arithmetic is independent of
whether gaps predict cuts.

**3. The one place the gap analysis clearly earns its keep is the writer, before
recording.** On the short, two scenes ran past M01's 12 s ceiling — s10 (the tell,
19.4 s) and s11 (the Meta payoff, 14.2 s) — and they are exactly the two blocks already
flagged as too long. Read as a *motion* problem that means "add a visual event." Read
as a *writing* problem it means "this paragraph carries more than one picture can
hold." The second reading is better and it costs a free scratch take.

## What I am NOT proposing

I drafted a pipeline change — cuts fall out of gaps, `retime_to_take` retires — on the
strength of test 1. **Test 2 does not support it and it is withdrawn.** A 44%-recall
signal is not a cut list.

## What is worth doing

- **Keep the gap census as a pre-record writing check.** Scenes over 12 s in the
  scratch take are paragraphs to split. Free, and it caught two real ones here.
- **Stop compressing inter-paragraph silence to hit a runtime.** It does not get there
  and it costs the re-time. Cut words instead — which is the standing Tokyo decision.
- **Test the real question on the next episode:** cut *on* the pause versus *through*
  it. That is an A/B by ear, not an arithmetic finding, and it is the part of the
  operator's observation this measurement could not settle.

## Method note

Test 1's data: `tokyo-tea-break/scratch/scratch-kokoro.words.json`.
Test 2's: `steel-and-paper/build-f/timeline.json` (processed clock, matched against the
scene table on the same clock) and `vo-f/audio/scene_*.words.json` (raw, for the
distribution). The processed timeline carries `dead_space_compressed: true`, which is
why the raw parts were pulled separately.
