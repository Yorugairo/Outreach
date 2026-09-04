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

## 46.3 The gap threshold is unsettled

`01` and the dossier's `gap_detector.py` blueprint use **Δt ≥ 0.45 s** and place the cut
at the gap's **midpoint** (`cut = word[i].end + gap·0.5`). `06` and `08` use **Δt ≥ 0.30 s**
and place it at gap **onset**.

These are different gates. **Settle from our own word timeline before M13 ships** — count
how many gaps each threshold yields across ep1 and whether the 0.45 s set is large enough
to carry every needed boundary.

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

## 46.6 Speech rate

Reference **183.6 WPM** overall; our ep1 measured 182.8. Our doctrine target is
**145–165 WPM**, which sits below both. Flagged for an operator decision — a gate that
neither we nor the best-performing reference satisfies is not describing the work.

## 46.7 Captions

Reference captions: bottom centre, **no container box, no frosted pill, no tint** — white
sans with a thin dark stroke and a drop shadow. This validates our floating-caption
treatment; it is a confirmation, not a change.

## 46.8 Sources

Primary: `04` (recomputed), `01`, `MASTER_RESEARCH_AND_EVIDENCE_DOSSIER.md` §10.
Our comparison data: `SHOT-TABLE-F.md`, `build-f/timeline.json`.
