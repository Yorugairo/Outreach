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

*Method caveat, stated because it matters:* their VTT carries word **onsets** only, so
their "gap" is an onset-to-onset delta and mine for ep1 was end-to-start. Their number
is therefore generous. The 0.17 s median cut-to-boundary distance is the harder
evidence, and it is not close.

## 2. The rhythm difference is variance, not rate

This is the part the dossier misses entirely, and it is more actionable than the cut
count.

| shot length | ep1 | tutorial |
|---|---|---|
| under 3 s | **3 (4%)** | **24 (31%)** |
| 3–8 s | 23 | 29 |
| 8–15 s | **38 (51%)** | 13 |
| over 15 s | 11 | 12 |
| median | **9.2 s** | **4.5 s** |
| cuts/min | 5.58 | 6.28 |

**We cut at nearly the same rate and with almost no variance.** Half of ep1 sits in an
8–15 s band; the tutorial punches (31% under three seconds) and then dwells (12 shots
over fifteen). Same CPM, completely different feel.

A flat nine-second rhythm reads as static even though the screen is technically
changing — which is E21's failure wearing a disguise our motion gate cannot see, because
M01 only asks "did something happen in the last 12 s," never "does the rhythm vary."

**We have three punch shots in thirteen minutes.** That is the gap.

## 3. They speak much slower

ep1 runs **182.8 WPM** (post tempo-edit). The tutorial runs **120–147 WPM**. Even
allowing that our figure is accelerated, the difference is large.

Instructional content buys processing time with pace. Ours spends it. Combined with
finding 1 — cuts landing mid-word — ep1 gives a viewer no seam anywhere: the words do
not stop and the pictures change inside them.

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
   declared. Mechanical, checkable, fails ep1 at 68%.
2. **Add a rhythm-variance check.** M01 asks whether *something* happened; nothing asks
   whether the cadence varies. A proposed shape: at least 20% of shots under 3 s, and no
   more than 40% inside any single 7-second-wide band.
3. **Author the shot table onto the gap list**, not onto the clock. Snapping an existing
   table recovers only a third of the cuts.
4. **Re-examine the tempo edit against pace.** We accelerate to 182 WPM; the reference
   that works sits at 120–147. That is a listen test, not an arithmetic one.

**Not to copy:** their six-phase story architecture (they have none — the dossier
invented it), their browser-extension queue (we have the MCP), or their cut *rate*
(ours is already comparable — it is the distribution that differs).
