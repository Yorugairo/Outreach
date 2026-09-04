# What we actually learn from the zapiwala tutorial — verified, 2026-09-04

Read against Gemini's dossier in this directory, then re-measured from the primary
artifacts (`video.en.vtt` word timings, `SHOT_LEDGER.md`) because three of the report's
headline numbers do not survive inspection. The **core learning is real and I confirmed
it independently**; the metrics around it need correcting before anyone cites them.

---

## 1. The finding that matters: they cut on the gap, we cut through the word

Their video's own edit, measured from its caption word timings against its own cut list:

| | ep1 (Steel and Paper) | the tutorial |
|---|---|---|
| **cuts landing in an acoustic gap** | **32%** | **82%** |
| cuts landing MID-WORD | **68%** | — |
| median distance, cut → nearest word boundary | — | **0.17 s** |

They practise what the video teaches. We don't, and nothing in our gate stack looks at
it. This is the same result our own independent test produced from
`FINDING-gaps-are-the-edit.md`, arrived at from the other direction.

**And Wealth Logic — the genre comparable — lands at exactly the same 82%**, median
0.16 s from a word boundary. Two channels, different formats, different pacing, same
number. Ours is 32%. This is the one finding that survived every control, and it is the
only measure on which we differ from the reference at all.

*Method caveat, stated because it matters:* their VTT carries word **onsets** only, so
their "gap" is an onset-to-onset delta and mine for ep1 was end-to-start. Their number
is therefore generous. The 0.17 s median cut-to-boundary distance is the harder
evidence, and it is not close.

## 2. RETRACTED — "cadence variance" was a tutorial artifact

My first pass claimed we lack rhythm variance because only 4% of ep1's shots run under
3 s against the tutorial's 31%. **The operator doubted it, and the control proves them
right.** Wealth Logic — one of the best-performing faceless finance channels, the
correct genre comparable — sits where we sit:

| | ep1 (ours) | Wealth Logic | tutorial |
|---|---|---|---|
| median shot | 9.20 s | **9.55 s** | 4.50 s |
| under 3 s | 4% | **6%** | 31% |
| 8–20 s | 56% | **55%** | — |
| mean shot | 10.75 s | **10.14 s** | 9.55 s |
| cuts/min | 5.58 | **5.93** | 6.28 |

We are within a few points of the reference on every measure. The tutorial's rapid
cutting is **format** — it is showing software steps on screen, where a click is a
beat. Reading it as a retention technique and importing it would have made our
explainers worse.

## 3. RETRACTED — "we speak too fast" was my parsing error

I measured both references at 120–156 WPM against ep1's 182.8 and concluded we rush.
**Wrong: my VTT parser undercounted.** YouTube's rolling captions repeat a tail of each
cue, and only some words carry `<c>` timestamps; a proper suffix-merge reconstruction
gives:

| | words | WPM |
|---|---|---|
| **ep1 (exact, from the take)** | 2,457 / 806 s | **182.8** |
| **Wealth Logic** | 3,101 / 1,013 s | **183.7** |
| tutorial | 1,832 / 744 s | 147.7 |

**We match the best-performing finance channel to within one word per minute.** Gemini's
report had 183.6 and was right; I was wrong. The tutorial is the slow outlier, again
because of format.

## 4. What their pipeline does that ours does not

- **Pause timestamps are extracted before scene generation**, and the prompt batch is
  generated *from* those timestamps (`frames/frame_0126.jpg`, the pause-extraction
  step). Scene count is an output of the audio, not an input to it.
- **Their own slide states the rule** (`frames/frame_0086.jpg`, "WRONG vs RIGHT"):
  scene generation is subordinate to voiceover timing.
- They queue Flow through a **browser extension with jitter**; we have the MCP server,
  which is strictly better and already built. Nothing to learn there.

## 5. Three errors in the dossier — do not cite these

| the report says | actual |
|---|---|
| 100 cuts, 8.03 CPM | **78 cuts, 6.28 CPM** — 22 entries are 0.1 s detector artifacts, not shots |
| phase paces of 250–311 WPM | **inflated 1.69×.** The phase word counts sum to 3,097 against the video's own 1,832: VTT rolling captions repeat each line, and the dedupe never reached the phase counter |
| a clean 6-phase retention architecture, incl. "P4 Pivot, 1 shot, 219 words" | **imposed, not found.** A how-to tutorial has no chiastic turn; P4's "pivot" is the step *"choose accuracy mode"*, and its transcript sample is a byte-for-byte duplicate of P5's |

The mean shot duration (7.47 s) and "46 under 3 s" are also artifact-inflated; corrected
figures are in §2.

## 6. What to actually do

1. **Ship gate M13** — a scene boundary lands in an acoustic gap ≥0.30 s or is
   declared. Mechanical, checkable, fails ep1 at 68%. **This is the whole finding.**
2. **Do not build a rhythm-variance gate.** I proposed one; the control retired it. Our
   distribution already matches the reference.
3. **Do not slow the narration.** We are at 182.8 against Wealth Logic's 183.7.
4. **Author the shot table onto the gap list**, not the clock. Snapping an existing
   table recovers only a third of the cuts.

**Not to copy:** the tutorial's cut rate or its six-phase reading. What we were missing
was one thing, and it is where the cut lands — not how often, not how fast we speak.

## 7. What is worth reading in Gemini's Wealth Logic report

That report is materially better than the tutorial one — its pace figure was right and
mine was wrong. Its shot-band claim overstates slightly (78% in 8–20 s; measured 55%),
but four takeaways in it are substantive and **unverified by me**, and they are about
composition rather than timing:

- **the unifying equation spine** — one mechanism evaluated across variants, against a
  list of six unrelated tips. That is a script-architecture claim worth testing on our
  own listicle-shaped drafts.
- **evidence screen time ~10 s**, which matches our own E25 hold ceiling.
- **one persistent diegetic host** and physical props — which is the actor decision we
  already made and are still executing.
- **kinetic floating captions with no background pill** — a direct comparison against
  our STAGE caption mode.

Those are the next things to check, and they are visual, so they need the frames rather
than the timings.
