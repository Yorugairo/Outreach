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

## Test 3 — the question I should have asked first

Tests 1 and 2 asked "do gaps predict where we cut." That was backwards. The claim is
not that gaps describe good editing; it is that **cutting anywhere else costs you** —
the transition should live inside the silence so the new visual is already established
when the next word lands. The testable version is their point 3: *do our cuts hit
mid-phrase?*

**They do. 68% of them.**

| where our 75 authored scene cuts land | |
|---|---|
| **MID-WORD** — inside a spoken syllable | **51 (68%)** |
| in a gap of any size | 24 (32%) |
| in a gap ≥0.45 s — their structural threshold | **10 (13%)** |

Cuts land inside `'same'`, `'fund,'`, `'getting:'`, `"isn't"`, `'overshoots.'`,
`'peak,'`, `'matched'`. This is ep1 — the episode whose retention we are still
explaining — and no gate we have looks at it.

### And the cadence was already right

| | |
|---|---|
| gaps ≥0.45 s in the take | **77** — one every 10.5 s |
| scenes we authored | **75** — one every 10.7 s |
| authored cuts within ±2 s of one | 27 of 75 |

The take offers almost exactly as many natural breakpoints as we cut, at almost exactly
our rate. **We are cutting at the right tempo and the wrong phase.** Snapping the
existing table fixes only about a third (36% at ±2 s tolerance, zero collisions), so
this is not a post-process — the shot table has to be authored *onto* the gap list,
which is their process.

One number reconciles this with our own doctrine: at 0.45 s the gaps arrive every
10.5 s, inside M01's 12 s ceiling. **Gap-anchored scenes satisfy the motion gate
naturally.** And note where those gaps come from — our own `insert_edit_pauses.py` put
15 of them there deliberately. We manufacture the breakpoints and then cut past them.

### The synthesis the operator named

> "We have a stronger process, but were primarily missing the idea of matching the
> natural rhythm to images, b-roll, evidence."

That is the right shape, and it resolves the apparent conflict with M01:

- **Scene CUTS snap to acoustic gaps.** One thought per shot; the transition happens
  while nobody is speaking.
- **Visual EVENTS inside a scene carry the motion** — dock rise, chart reveal, ledger
  unroll, Ken Burns, caption pop. M01 counts these, not only cuts, so a 10 s
  gap-anchored scene with a dock at its midpoint is denser than a 10 s arbitrary cut.

Their process stops at "cut on the gap." Ours adds what fills the shot between cuts —
which is the part worth keeping.

## Proposed gate — M13

> **A scene boundary must land in an acoustic gap ≥0.30 s, or be declared.**

Mechanical, checkable from the word timeline, and it would have failed ep1 at 68%.
Declared exceptions exist — a hard cut *through* speech is a legitimate momentum move —
but it should be a choice on the record, not the default 51 times.

## What I am NOT proposing

I drafted a pipeline change on test 1 — cuts fall out of gaps automatically,
`retime_to_take` retires. **Still withdrawn.** Test 3 changes the argument for
gap-anchoring but not the mechanism: gaps are where a cut should *land*, not a
generator that decides *how many* scenes there are or what is in them. The shot table
stays authored. It is authored onto the gap list instead of onto the clock.

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


## Reference-first — 2026-09-04

The tests above measured ourselves. The operator's correction: *"is basing the gap threshold
off our own work really the right way?"* It is not — our practice is the thing under
suspicion. So the reference was measured the same way (its audio through local Whisper, its
99 cuts from the frame-accurate ledger), and ours re-measured through the same aligner:

| measured through the same Whisper pass | Wealth Logic (99 ledger cuts) | Steel and Paper (103 scene starts + dock enters) |
|---|---|---|
| cuts that land **mid-word** | **15–25 %** (tolerance 0.10 / 0.05 s against the ledger's 0.1 s precision) | **39–42 %** |
| cuts inside a gap **≥ 0.30 s** | **72–81 %** | 52–54 % |
| cuts inside a gap ≥ 0.45 s | 49–56 % | 42–43 % |
| where the cut sits inside its gap (median, 0 = onset, 1 = next word) | **0.80–0.83** | 0.46 |
| gaps ≥ 0.30 s available per minute | 17.9 | **21.4** |
| words per minute | 187 | 177 |

**Settled (46 §46.3):** threshold 0.30 s; the cut sits at ~0.8 of the gap, just before the
next word; a mid-word share above 25 % is a FAIL. And the standing Tokyo decision — *cut
words rather than re-time* — is confirmed from the other side: the slots exist (21 per
minute at ≥ 0.30 s); the cuts are simply not placed in them.

Script: `content/video_engine/scripts/measure_cut_gaps.py --words <words.json> --cuts <ledger.md | timeline.json>`.
