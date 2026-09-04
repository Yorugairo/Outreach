# Response to research pass 1 — what closed, what reopens

**To:** the research layer (Gemini deep-research pass)
**Re:** `ANSWERS-RESEARCH-BRIEF-animation-craft.md`, 2026-09-04
**Reviewed:** answers file in full; `07_academic_literature...` spot-checked; one code
claim verified against the source file. Bundle files 01–06 and the two index documents
were **not** reviewed — nothing in them is accepted or rejected by this response.

---

## 1. The headline, stated fairly

**Most of the mechanism work is correct and is being adopted.** The two-thirds power
law, ARAP, the five constraints, the frame-metric set, Kubelka-Munk, Lakoff, and the
closed-form oscillator argument all hold up and several answer questions we could not
have answered ourselves. That is a real result.

**A specific and repeated defect blocks the rest: real papers were attached to numbers
that did not come from them.** Not hallucinated papers — every one of the 20
bibliography entries is genuine. The failure is in the join between the number and the
citation.

**Part of this is our fault, and naming it should make the correction easier.** Our
brief demanded that every finding arrive as "a number with a tolerance and its
condition." That contract created pressure to fill every slot with a number. The
evidence that the pressure caused the defect is in your own bundle: the academic
monograph (07), written under no such contract, is disciplined throughout — Kubelka-Munk
correctly stated as two-flux radiative transfer, Deegan correctly used for contact-line
deposition, Viviani correctly used for the power law, and almost no free-floating
percentages. The answers file (08), written under the contract, is where numbers were
invented. **The contract asked for a form and got the form.**

So the rule changes rather than tightens:

> **"We could not find a measured value" is a passing answer.**
> **A fabricated value is a failing one.**
> An honest gap is more useful to us than a filled slot, because we build gates on these
> numbers and a gate built on an invented threshold silently passes bad work forever.

---

## 2. CLOSED — accepted, do not redo

Effort spent re-researching these is wasted. They are being built.

| item | what was accepted |
|---|---|
| **A5** | The two-thirds power law, `v(s) = γ·κ(s)^(-1/3)`, Viviani & Terzuolo 1982. Correctly stated, correctly cited, correct curvature formula. **This is the single most valuable result of the pass** — it is the actual answer to why our progressive stroke reads as a sliding mask. |
| **E1** | The four-metric set: motion energy, centroid of change, Itti-Koch saliency, Farnebäck optical-flow coherence. The *metrics* are accepted; the pass ranges are not (see §3). |
| **E2** | Stroboscopic aliasing as the mechanical cause of "the race feels choppy," with Watson/Ahumada/Farrell 1986 correctly applied. This converted an operator ear-verdict into a measurable cause, which is exactly what was asked. |
| **C1** | ARAP shape interpolation; polar decomposition `J = R·S`, `det(J) > 0` against collapse. Alexa/Cohen-Or/Levin 2000, Igarashi 2005. |
| **C2** | The five constraints — Parent, AimAt, PathFollow, DistanceLimit, DriverExpr. Correct minimal vocabulary. (The "95% of moves / under 200 lines" figures are ignored; the set is what matters.) |
| **D5** | Lakoff & Johnson as the derivation base for the prop library. |
| **§0.1-4** | Closed-form damped-oscillator solutions for O(1) seek-safety under parallel frame rendering. Correct and materially important to our renderer. |
| **07 monograph** | Kubelka-Munk 1931 for layered ink (correctly identified as the answer to why alpha blending looks sterile), Deegan et al. 1997, Chu & Tai, Euler spirals, BBW, DQS. Clean work. |

## 3. RECLASSIFIED — kept, but relabelled as proposals

These are being used. They are **not** being recorded as findings, and no paper will be
cited for them. No re-research needed unless you can supply a real locator.

A1's timing chart · A2's ease mappings · A3's material spring parameters · A6's
secondary-motion budget (the 0.22 energy ratio) · A5's nib-pooling law `w ∝ v^(-0.25)`
(an engineering extension of the power law, not part of it) · B2's shot-length floors ·
**E1's threshold ranges** (`0.012 ≤ ME ≤ 0.28`, `ΔC ≤ 280 px`).

E1's thresholds specifically: these have to be measured against our own footage and the
reference channels. Adopting a guessed threshold would commit exactly the error the
metric set exists to detect.

---

## 4. REOPENED — four items, with acceptance criteria

### RE-ASK 1 — A4, "the threshold of alive" ★ highest priority

**What was wrong.** The entire section rests on *Mackworth 1948*, cited for: "after
1.2 s of absolute zero pixel movement, ocular saccade frequency drops by 45%; by 2.5 s,
visual fixation degrades by >80%." Mackworth 1948 is the Clock Test — **vigilance
decrement in a radar-watch task measured over roughly thirty minutes to two hours**. It
is three orders of magnitude off the timescale it is cited for, and the 45% and 80%
figures are not in it. Mackworth is also **the one citation absent from your own
bibliography**, which is the tell we now check for.

**Why this one matters most.** Two of our shipped gates (E21 "screen never still", M10
"no still over 6 s in the first minute") rest on this question. They are currently
operator-derived by eye. We asked whether there is a measured basis, and the answer came
back invented — which is worse than the honest "no," because we nearly encoded it.

**A passing answer is either:**
- (a) a measured result about attention or fixation on a **held static frame inside
  moving video**, with a retrievable locator — page or section, or a URL; **or**
- (b) an explicit statement that no such measurement exists, followed by the nearest
  adjacent evidence, each item labelled with **how far it sits from our question**
  (different task, different timescale, different medium).

Answer (b) is fully acceptable and we would rather have it than anything approximate.

**Leads, unverified — check these, do not assume them.** Motion-onset attention capture
(the finding that a newly-moving object involuntarily pulls gaze); the scanpath and
fixation-evolution literature on static images in the Buswell/Yarbus lineage; any
platform or broadcast research that actually timed hold length against viewer drop-off.
We have not verified that any of these say what we hope; they are search directions.

### RE-ASK 2 — the Potter misuse (affects A1 and B2)

**What was wrong.** Potter et al. 2014 is cited for a minimum 8-frame (333 ms)
recognition hold and a "≤4 frames reads as a flash" boundary. Potter's finding is that
**meaning is detected at 13 ms** — about one third of a single frame at 24 fps. The
paper argues against the floor it was recruited to certify.

**A passing answer distinguishes three different thresholds**, which the section
conflates: *detection* (Potter's ~13 ms), *comprehension* (identifying what the thing
is), and *comfortable reading* (parsing a multi-digit number or a chart without
strain). Our shot-length floors depend on the third. Give each its own value and its own
source, or state plainly that only the first is measured and the other two are craft.

### RE-ASK 3 — the two 38% statistics

"Elevating cognitive workload by 38% (Sweller 2011)" and "saves 38% cognitive
split-attention." Split-attention and cognitive load theory are real; the 38% is not
from Sweller or Mayer, and Sweller does not appear in the bibliography. **Source them or
delete them.** A qualitative claim ("split attention raises load") needs no number and
would have passed unchallenged.

### RE-ASK 4 — B1, which did not answer the question asked

**What was wrong.** B1 restates **our own** measurement (82% of reference cuts in
acoustic gaps vs 32% on ep1 — that number came from us, in the brief) and supplies a
mechanism for it. The question was whether the gap-cut rule exists **independently in
the literature**. Your own `[VERIFY-01]` flags this honestly, which we credit.

**A passing answer:**
- separates **practitioner doctrine** from **measured result**. Murch's *In the Blink of
  an Eye* is a valuable and influential essay; it is not a measurement, and it should be
  labelled as doctrine.
- finds the empirical film-cognition work on **whether viewers actually detect cuts**,
  and what makes a cut detectable or invisible. This literature exists.
- states whether the acoustic-gap alignment specifically has ever been measured, or
  whether our 82/32 is the only measurement of it in the world. Either answer is useful;
  the second would be a genuine finding.

**Lead, unverified:** the film-cognition work on edit detection and on attentional
continuity across cuts. Check it; do not assume it says what we want.

### RE-ASK 5 (procedural) — claims about our code

The parallax finding asserted that `tools/google-flow-driver/src/parallax-runner.mjs`
line 142 maps `strength` to raw intensity, and that the model should change from
`vitl_fp32`. Opening the file: it is 233 lines, there is no such line 142, `intensity`
is **hardcoded to `1.0` in all six preset blocks** (lines 34–110), and the configured
model is `depth_anything_v2_vits_fp16`, not `vitl_fp32`.

**The defect you identified is real and is in fact worse than reported** — full credit
for finding it. But the coordinates were invented around a correct intuition, and a fix
instruction with a wrong line number and a wrong current-value costs more than it saves.

**Rule: a claim about our code quotes the file, the actual line number, and the actual
current text, read from the file.** If the file was not opened, say the defect is
suspected and name what to check.

---

## 5. The operating contract, revised

Replacing the sourcing clause in the brief:

1. **Every number carries a retrievable locator** — page or section of the cited work,
   or a URL. Not just an author and a year.
2. **A number with no locator is a design proposal and must be labelled as one.**
   Proposals are welcome and useful. Proposals wearing citations are not.
3. **The bibliography certifies nothing about the body.** Checking that the papers are
   real is not the check. Every one of your twenty was real; the join was the problem.
4. **An honest gap beats a filled slot.** "No measured value exists; here is the nearest
   adjacent evidence and how far it sits from the question" is a passing answer.
5. **Distinguish doctrine from measurement.** Practitioner sources (Williams, Murch,
   Lasseter) are valuable and we want them — labelled as craft doctrine, not as data.
6. **Claims about our code are read from the file**, with real line numbers.

## 6. Priority for pass 2

1. **A4** — re-ask. Two shipped gates depend on it and it is currently unsupported.
2. **B1** — the actual question: does the gap-cut rule exist outside our own measurement?
3. **A1/B2** — the three thresholds separated (detection / comprehension / comfortable
   reading), which is what our shot-length floors actually need.
4. Anything in §3 you can attach a real locator to. Optional; they are usable as
   proposals meanwhile.

Everything in §2 is closed. Do not spend a second pass on it.
