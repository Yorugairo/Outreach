# 46 — Reference rhythm: what the shot ledger actually measures

Extracted from `04_shot_ledger_100_cuts.md` (primary measurement, recomputed here) and
`01_wealth_logic_production_report.md`. Status: **reference — not yet folded to
portable.**

Reference: *Wealth Logic*, "6 Ways Rich People Make Money With Debt", 16m53s, 100 shots,
262k views. Comparison: our *Steel and Paper* ep1, 13m26s, 75 shots.

---

## 46.1 The distribution — recomputed from the ledger, not quoted

| | reference | ours |
|---|---|---|
| runtime | 1013.6 s | 806.5 s |
| shots | 100 | 75 |
| **cuts / min** | **5.9** | **5.6** |
| mean | 10.1 s | 9.5 s |
| median | 9.6 s | 9.7 s |
| **Q1 / Q3** | **6.3 / 13.2 s** | **7.6 / 11.0 s** |
| **IQR** | **6.9 s** | **3.4 s** |
| longest | 26.0 s | 19.1 s |
| shortest | 1.6 s | 1.7 s |
| ≥ 6 s | 80 % | 88 % |

**We cut at the reference's rate.** Means, medians and CPM are within noise. The
difference is entirely in **spread: our interquartile range is half theirs.**

> **We hold the right average with the wrong distribution. We metronome; they vary.**

A 26-second hold and a 1.6-second punch inside one episode is a rhythmic instrument we do
not currently play. Target the distribution, not the mean.

**Which distribution.** Cutting, Brunick & DeLong (2011) find Hollywood shot durations are
**log-normal** — a long right tail of occasional very long holds, not a symmetric spread.
That is the shape the reference has (median 9.6 s, max 26.0 s) and the shape we lack
(median 9.7 s, max 19.1 s). So the target is not "vary more" in both directions: it is
**keep the median and grow the tail** — earn a small number of much longer holds.
*Claim sourced to Cutting 2011 via the dossier; the log-normal fit has not been tested
against our own or the reference's data — that test is one line once we want it.*

## 46.2 What this means for M13 and for M10

**M13 (cut lands in an acoustic gap) is free.** Since our cut *frequency* already matches,
landing cuts in gaps costs nothing structurally — it is pure placement. Our 68 % mid-word
rate is not a symptom of over-cutting.

**M10 is already correct — an earlier claim here that it was not is withdrawn.**
The reference's first minute runs `10.6, 15.6, 6.0, 3.7, 13.5, 3.7, 2.9, 14.9 s`, five of
eight shots past six seconds, which looks like it should fail a "no still over 6 s" gate.
It does not: `gate_motion_density.py:277` computes a still stretch as the gap between
**visual events** — dock entries, badge lights, caption beats, species firings — not
between shots. A 15.6 s shot with a dock at +4 s and a callout at +9 s passes cleanly, and
that is exactly E21's intent. Shot length has its own separate ceiling
(`PLATE_HOLD_MAX_S = 20.0`, with a two-dock escape), which the reference also clears.
**The system already distinguishes "the screen went still" from "the plate held long."**
See [47-FINDINGS-TO-CHECKS](47-FINDINGS-TO-CHECKS.md) §0.

## 46.3 The gap threshold — settled from the reference, 2026-09-04

`01` and the dossier's `gap_detector.py` blueprint used **Δt ≥ 0.45 s** and the gap's
**midpoint**; `06` and `08` used **Δt ≥ 0.30 s** and gap **onset**. An earlier draft of this
section proposed settling it from our own word timeline. **Operator: *"is basing the gap
threshold off our own work really the right way? We should check Wealth Logic's gap
threshold and compare against ours."*** So it was measured on the reference — its audio
through local Whisper (`small.en`, word timestamps), its 99 cuts from the frame-accurate
ledger (`04_shot_ledger_100_cuts.md`) — and ours the same way (`measure_cut_gaps.py`):

| measured through the same Whisper pass | Wealth Logic (99 ledger cuts) | Steel and Paper (103 scene starts + dock enters) |
|---|---|---|
| cuts that land **mid-word** | **15–25 %** (tolerance 0.10 / 0.05 s against the ledger's 0.1 s precision) | **39–42 %** |
| cuts inside a gap **≥ 0.30 s** | **72–81 %** | 52–54 % |
| cuts inside a gap ≥ 0.45 s | 49–56 % | 42–43 % |
| where the cut sits inside its gap (median, 0 = onset, 1 = next word) | **0.80–0.83** | 0.46 |
| gaps ≥ 0.30 s available per minute | 17.9 | **21.4** |
| words per minute | 187 | 177 |

**Three things settled, none of them what either report guessed:**

1. **The threshold is 0.30 s.** 0.45 s would exclude nearly half of the reference's own
   cuts. Their in-gap cuts sit in silences of 0.42 / 0.48 / 0.64 s (p25/p50/p75), with a
   p10 of 0.36 s — 0.30 is the floor that keeps them all.
2. **The cut lands late in the gap, not at its onset and not at its midpoint** — median
   0.8 of the way through the silence, i.e. just before the next word begins. The picture
   changes as the next phrase arrives. `cut = gap_start + 0.8 · gap`.
3. **We do not lack slots; we ignore them.** With the same aligner we have *more* gaps
   ≥ 0.30 s per minute than the reference (21.4 vs 17.9) and still put 4 in 10 cuts inside
   a word. The earlier "our delivery has fewer pauses" read was an aligner artifact — the
   ElevenLabs alignment abuts words that Whisper separates.

**M13 as it will ship (47 §2):** every cut within 0.05 s of a gap ≥ 0.30 s or FAIL, placed
at 0.8 of the gap; a mid-word share above **25 %** FAILs the build (the reference's own
ceiling at the ledger's precision). Data: `sources/reference_analyses/6-ways-…/audio/
wealth-logic-6-ways.words.json` (committed) and `build-f/episode-paused.whisper.words.json`.

## 46.4 The equation spine — the script-architecture finding

The reference covers six mechanisms and never reads as a listicle, because it is **one
equation evaluated six times**:

```
Spread = (Rate of Return − Cost of Debt) × Leverage
```

introduced in P1 as "the one number," then each mechanism is the same equation with
different variables: trade credit (cost 0 %, leverage ∞) · cash-out refi ·
buy-borrow-die · SBLOC (plus its margin-call guardrail) · 0 % balance transfer · credit
score as the cost lever. **P6 closes by restating the equation.**

The ring is not a phrase coming back — it is **the mechanism coming back**. That is a
stronger ring than a repeated line and it is what our re-scripts should aim at.

## 46.5 The phase map

```
00:00 [P1 Open] 01:30 [P2 Engine] 02:52 [P3 Gap] 07:36 [P4 Pivot] 09:17 [P5 Payoff] 14:21 [P6 Close] 16:53
```

The pivot lands at **45 %** of runtime, inside our chiastic 45–55 % window. Phase
*boundaries* are usable.

**Phase word counts in `01` are not.** They sum to 3952 against a stated 3101 total and
imply an unspeakable 299 WPM in P1 — the known YouTube caption over-count (rolling
carryover), already run down by the operator. Use the boundaries; ignore the per-phase
word and WPM figures.

## 46.6 Speech rate — and a number I invented

Reference **183.6 WPM** overall; our ep1 measured 182.8. Those two are real measurements.

**RETRACTED 2026-09-04: the "145–165 WPM doctrine target" was mine, not the doctrine's.**
The operator asked where it came from and it has no origin. Every occurrence in the repo
traced back to this line, then to the backlog and one finding doc that both cited *this
line* — a citation loop with nothing at the centre.

**What the doctrine actually contains is 140 WPM, and it is not a delivery target:**

| where | what it says |
|---|---|
| `02-CONTENT-STRATEGY.md` | "short sentences (**140 WPM basis**)" — for planning pauses |
| `04-STORYBOARD-CONTRACT.md` | `"wpm_target": 140`, and explicitly: ***"`timing.target_s` is an estimate, not a promise"*** — used so the guard can check duration fit *before* spending on TTS |
| `06-SCRIPT-TRANSFORMATION-SPEC.md` | "Length + pacing math (**140 WPM basis**)" |
| `19-HYPERFRAMES-LANE.md` | "Deterministic **estimated** timings (140 wpm)… **provisional by definition; never publishable**" |

**140 is a length-estimation constant** — word count → runtime guess before recording. It
was never a rate anyone was asked to deliver at, and the renderer obeys the *measured*
duration regardless.

**So there is no contradiction to resolve.** An estimation constant and an actual delivery
rate are different kinds of number; they were never in tension. Backlog B5 is withdrawn.

**Operator, 2026-09-04:** we run closer to **180** than to 145.

*Lesson, and it is the one this document spent the day applying to other people's work: a
number with no locator, repeated across three documents, starts to look sourced. The check
is `grep` for its origin, not a recollection that it feels right.*

## 46.7 Captions

Reference captions: bottom centre, **no container box, no frosted pill, no tint** — white
sans with a thin dark stroke and a drop shadow. This validates our floating-caption
treatment; it is a confirmation, not a change.

## 46.8 Sources

Primary: `04` (recomputed), `01`, `MASTER_RESEARCH_AND_EVIDENCE_DOSSIER.md` §10.
Our comparison data: `SHOT-TABLE-F.md`, `build-f/timeline.json`.
