---
id: P40-MEASURE-THE-FIRST-MINUTE
title: Point an instrument at our own output - the E1 metrics against the one retention curve we hold
status: draft
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-04
updated: 2026-09-04
---

# Measure The First Minute

## Summary

The operator's standing frame is *we lose people in the first minute*. **Every claim I
have made about why is an inference** — from shot tables, gap percentages and reference
comparisons. We have never pointed an instrument at our own output.

We are not starting from zero. Two things already exist:

- **One retention curve**, and `SCRIPT-G-VIEWER-CALIBRATION.md` locates the drop at
  **0:45–1:00** (window w3).
- **The analytics behind it** (50, added 2026-09-04): the **cold cohort averages 1:05**
  against **4:39 overall**, and **75.2 % of watch time is a phone**. Because average view
  duration includes the viewers who stayed, the mass departure is *earlier* than 1:05.
- **A candidate root cause that outranks the metrics** (50 §50.2): 14 of 16 template font
  sizes render below 12 px in YouTube's default portrait player. **Check X0 before
  building any of this** — if the type is unreadable, no motion metric will explain the
  drop, and the fix is a font scale rather than a harness.
- **P36's finding**: confusion tracks that drop; information gain does not.

So this is not "measure everything and hope." It is one labelled example and a specific
question: **does any computable frame metric separate the window where we lose them from
the windows where we do not?**

This also settles **X3** (the gap threshold), which unblocks M13 — and X3 is free, needs
no render, and can run first.

## Intent And Acceptance

**Intent.** Build the E1 metric harness, run it over our own render against the known drop window, and settle the gap threshold — **after X0 has ruled the legibility explanation in or out.** The target is not "the first minute" but *the cold cohort's first ~60 seconds on a 390 px screen*.

**Acceptance:**

1. `gate_gap_threshold.py` reports, from ep1's word timeline, how many boundaries each
   candidate yields — **0.30 s at onset vs 0.45 s at midpoint** — and whether the 0.45 s
   set is large enough to carry every scene boundary the shot table needs. **X3 answered,
   M13 unblocked.**
2. The four E1 metrics compute over a rendered frame sequence: motion energy, centroid of
   change, Itti-Koch saliency, Farnebäck optical-flow coherence.
3. A report gives each metric's distribution across ep1's opening, **with the 0:45–1:00
   window called out against the rest.**
4. The report states plainly, for each metric, whether it separates that window — and
   **"no metric separates it" is an accepted, expected result** worth having.
5. Every threshold the report proposes is labelled a **hypothesis from n=1**, never a
   gate-ready number.

**Anti-goals.** No threshold promoted to a gate from one episode. No temporal comparison
against the reference channel (see Not Building). No claim that a metric *explains* the
drop — correlation on one curve is a lead, not a cause.

## Scope

`content/video_engine/scripts/metrics/`, `content/video_engine/tests/`, and one report
artifact under the ep1 build.

## Not Building

- **Temporal metrics on the reference channel.** We hold **310 sampled keyframes**, not
  video. Motion energy between irregularly-sampled keyframes is not comparable to motion
  energy between consecutive video frames, and pretending otherwise would manufacture a
  false comparison. Frame-level statistics (saliency, contrast, composition) are
  computable on the samples; temporal ones are not. **Re-acquiring the reference video is
  a separate decision, recorded in the report.**
- **Any gate.** This produces measurement and hypotheses. Gates come after a second
  labelled curve exists.
- **Retention prediction.** One curve cannot validate a predictor.

## Human Gates

| gate | why |
|---|---|
| **Before any threshold enters a gate** | n=1. The report proposes; promotion needs a second episode's curve. This is the gate that stops today's error — inventing a threshold — from recurring in numeric clothing. |
| **Reference video re-acquisition** | A download decision with a cost, and it may not be needed if our own metrics separate the window. |

## Mandatory Reads

- [`docs/runbooks/PRP_EXECUTION.md`](../../../docs/runbooks/PRP_EXECUTION.md)
- `content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-G-VIEWER-CALIBRATION.md` — the retention curve and the w3 drop
- [`47-FINDINGS-TO-CHECKS.md`](../../../docs/content-video-engine/47-FINDINGS-TO-CHECKS.md) §2 — why E1's thresholds were deliberately *not* adopted from the research
- [`46-REFERENCE-RHYTHM.md`](../../../docs/content-video-engine/46-REFERENCE-RHYTHM.md) §46.3 — the two gap-threshold candidates and where each came from
- `content/video_engine/scripts/viewer_windows.py` — P36's windowing, which this must match so the two instruments agree on window boundaries

`backend-patterns` / `frontend-patterns` not routed: CLI analysis over frames and JSON.

## Execution Path

| slice | route | why |
|---|---|---|
| T1 | `junior_developer` | pure JSON analysis, exact acceptance, no dependencies |
| T2 | `implementation_luna` | bounded; new dependency needs installing |
| T3 | **parent** | the interpretation is the deliverable and it is easy to over-claim |

## Patterns To Mirror

- **`viewer_windows.py`** — P36 already windows the episode. This uses the same boundaries
  so the perception test and the frame metrics can be read side by side.
- **`gate_motion_density.py`'s report format** — verdict, value, and the ruling it serves.
- **`46-REFERENCE-RHYTHM.md` §46.1** — the shot-distribution work is the template for
  honest measurement: recompute from primary data, state the comparison, and say plainly
  when it kills your own hypothesis.

## Task Slices

### T1: settle the gap threshold - X3
- Status: pending
- Owner: junior_developer
- Depends on: none
- Write set: `content/video_engine/scripts/gate_gap_threshold.py`, `content/video_engine/tests/test_gap_threshold.py`
- Acceptance: from `build-f/timeline.json`'s word list, count acoustic gaps at **≥0.30 s** and **≥0.45 s**; for each, report how many shot-table boundaries could land in one, and the mean distance from a boundary to its nearest gap. Report onset vs midpoint placement. **Deliverable is a recommendation with its numbers**, not a preference. Runs today with no render and no new dependency.
- Validate: `python content/video_engine/scripts/gate_gap_threshold.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f`
- Evidence: pending

### T2: the E1 metric harness
- Status: pending
- Owner: implementation_luna
- Depends on: P39 T2 (deterministic render) for the frames
- Write set: `content/video_engine/scripts/metrics/frame_metrics.py`, `content/video_engine/tests/test_frame_metrics.py`
- Acceptance: the four metrics compute over a frame directory. **OpenCV is not currently installed** — the slice adds it as an explicit dependency or implements the two cheap metrics (motion energy, centroid of change) in numpy and defers saliency and flow. Tests use synthetic sequences with known answers: a static pair gives zero motion energy; a translating block gives a centroid shift equal to its translation.
- Validate: `python -m pytest content/video_engine/tests/test_frame_metrics.py -q`
- Evidence: pending

### T3: run it against the drop and report honestly
- Status: pending
- Owner: parent
- Depends on: T1, T2
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/FIRST-MINUTE-MEASUREMENT.md`
- Acceptance: metrics across ep1's opening, windowed to match `viewer_windows.py`, with **w3 (0:45–1:00) called out against its neighbours**. For each metric: does it separate w3, and by how much. Cross-read against P36's finding that confusion tracks the drop. **Every number labelled hypothesis-from-n=1.** If nothing separates, the report says so and that is the finding — it would mean the drop is not visually-legible in these metrics and the cause is in the script or the package instead, which is itself worth knowing.
- Validate: operator reads the report and can state what it found without reading code
- Evidence: pending

## Verification

```powershell
python content/video_engine/scripts/gate_gap_threshold.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f
python -m pytest content/video_engine/tests/test_gap_threshold.py content/video_engine/tests/test_frame_metrics.py -q
python scripts/prp_validate.py .claude/PRPs/plans/P40-MEASURE-THE-FIRST-MINUTE.plan.md
```

## Evidence And Handoff

- T1's output settles X3 and unblocks P37's M13. **It is the cheapest useful thing in the
  whole stack** — no render, no dependency, runs today.
- T3's report is the first time we will have measured our own output rather than reasoned
  about it.
- **The honest expected outcome is that one curve is not enough**, and the report's real
  product may be a specification for what to capture on the next episode so that n=2 can
  actually settle something.
