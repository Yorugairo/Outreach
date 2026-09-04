# Extraction verdict — the animation-craft research pass

Reviewed 2026-09-04 against [`ANSWERS-RESEARCH-BRIEF-animation-craft.md`](ANSWERS-RESEARCH-BRIEF-animation-craft.md).
Nothing enters doctrine until it clears this triage. Same rule as a script figure:
**point at the artifact, not the claim.**

## The one-line read

**Strong on mechanism, unreliable on magnitude.** Where the pass names a real
physical or mathematical model, it is correct, correctly cited, and immediately
buildable — that half is worth the whole exercise. Where it emits a number with a
tolerance, the number is usually a design choice wearing a citation.

### The process lesson, which is the most valuable thing here

My output contract demanded numbers with tolerances. It got numbers with tolerances.
**The form was satisfied without the sourcing.** That is the same failure we already
solved once — a script asserting a figure with no fetch date — and the fix transfers:

> **A number must trace to a retrievable page, not to a bibliography entry.**
> A list of twenty real papers at the bottom does not certify the numbers in the body,
> because the numbers were not taken from those papers.

All 20 bibliography entries are genuine, correctly-formatted, real papers. That is not
the same as the claims being sourced, and checking the bibliography is not the check.
The next research pass gets this rule in the brief.

---

## ADOPT — mechanism real, cited correctly, buildable now

| # | finding | status |
|---|---|---|
| **A5** | **The two-thirds power law.** Pen speed couples to path curvature: `v(s) = γ·κ(s)^(-1/3)`, with the standard curvature formula. Viviani & Terzuolo 1982, Flash & Hogan 1985 — real, correctly stated, correctly applied. | **The single best result in the pass.** Directly implementable on `drawOn(path, k)`; it is exactly the answer to "why does our stroke read as a sliding mask." |
| **E1** | **Four computable frame metrics** — motion energy, centroid of change, Itti-Koch saliency, Farnebäck optical-flow coherence. All real, all available in OpenCV. | **Closes the blindness gap.** Adopt the metric set; **derive our own thresholds** from ep1 + the references (see below). |
| **E2** | **Stroboscopic aliasing as the diagnosis of "the race feels choppy."** Displacement per drawing step above ~12 px splits a moving object into ghosts; Watson/Ahumada/Farrell 1986 window-of-visibility is correctly applied. | An operator ear-verdict converted to a mechanical cause. This is precisely what E2 asked for. |
| **C1** | **ARAP for shape interpolation** — Alexa/Cohen-Or/Levin 2000, Igarashi 2005. Polar decomposition `J = R·S`, `det(J) > 0` to prevent collapse. | Correct method, correct citations. The object → chart morph rests on this. |
| **C2** | **The five constraints** — Parent, AimAt, PathFollow, DistanceLimit, DriverExpr. | Correct minimal vocabulary; matches what Rive and AE actually expose. Build this. (The "95% of moves / under 200 lines" is invented precision — ignore the numbers, keep the set.) |
| **D5** | **Lakoff & Johnson conceptual metaphor** as the base for the prop library (*more is up*, *limits are barriers*, *change is motion*). | Real, and it is the thing that turns the prop library from invention into derivation. |
| **§0.1-4** | **Closed-form damped-oscillator solutions for seek-safety.** Iterative integrators drift and force sequential evaluation; the analytic solution is O(1) at any frame. | Mathematically correct and materially important to our deterministic render. |

## ADOPT AS OURS — sound engineering, but a design choice we own and tune

These are not findings. They are reasonable starting constants. Take them, label them
as ours, and calibrate. **Do not cite a paper for any of them.**

- **A1** the timing chart (anticipation / travel / overshoot / settle by implied mass). Plausible craft values, no source. Note the heavy row's short settle is physically right — heavy reads as overdamped, fewer oscillations — but that reasoning is mine, not the pass's.
- **A2** ease mappings, **A3** material spring parameters, **A6** the secondary-motion budget (the 0.22 energy ratio is invented; the *shape* — secondary lags primary 2–4 frames and dissipates faster — is standard craft).
- **A5's nib-pooling law** `w ∝ v^(-0.25)`. An engineering extension of the power law, not part of it. Good idea; our constant.
- **B2** shot-length floors.
- **E1's thresholds** (`0.012 ≤ ME ≤ 0.28`, `ΔC ≤ 280 px`). These must come from measuring our own footage against the references — the same way the WPM finding was settled. Adopting someone's guessed threshold would repeat the error the metrics exist to catch.
- **The parallax intensity clamp.** *The defect is real and worse than described* — `intensity` is hardcoded `1.0` in all six presets of `tools/google-flow-driver/src/parallax-runner.mjs`, with `strength` defaulting to `1.0`. But there is no line 142, and the model in the file is `depth_anything_v2_vits_fp16`, not the `vitl_fp32` the pass claims to be replacing. `0.12` is a guess. **Recommendation: clamp it, but pick the value from a test roll, and leave the model choice alone until someone A/Bs it.** Not changed here — it alters render output and belongs to the Flow/parallax lane.

## REFUSE — the citation does not support the claim

| claim | why it is refused |
|---|---|
| **All of A4 — "the threshold of alive."** `τ_decay = 1.25 s`; "after 1.2 s of zero motion saccade frequency drops 45%; by 2.5 s fixation degrades >80% (Mackworth 1948 Clock Test)." | **Mackworth 1948 is a vigilance-decrement study over a 30-minute-to-2-hour watch**, measuring missed signals by a radar operator. It is three orders of magnitude off the timescale claimed, and the 45% / 80% figures are not in it. Mackworth is also the one citation **absent from the pass's own bibliography** — the tell. A4 is our highest-stakes section (E21, M10 rest on it) and it came back empty. **Re-ask it.** |
| **Potter et al. 2014 supporting an 8-frame (333 ms) recognition floor**, and "≤4 frames registers as a flash." | Potter found meaning **is** detected at **13 ms** — about a third of one frame at 24 fps. The paper argues the opposite of the floor it is cited for. The 8-frame number may still be sound craft; it is not Potter's, and cannot be presented as sourced. |
| **"38% cognitive workload (Sweller 2011)"** and **"saves 38% cognitive split-attention."** | Invented statistics. Split-attention and cognitive load are real (Sweller, Mayer); the 38% is not from them, and Sweller does not appear in the bibliography either. |
| **B1 as independent confirmation of the gap-cut rule.** | It restates **our own** 82% / 32% measurement back to us and supplies a mechanism. The mechanism (saccadic suppression, Bridgeman 1975) is real; Murch's blink thesis is essayistic, not a measured result. **The question I asked — is this a known rule in the literature — is still open.** The pass's own `[VERIFY-01]` flags this honestly. |

## What to do next, in order

1. **Build A5.** The curvature-coupled draw rate on `drawOn`. Highest value, lowest risk, fully sourced. It is backlog A1's renderer work and the ink problem (C5) at once.
2. **Build E1 as a measurement script, not a gate.** Run the four metrics over ep1, the Tokyo cut, and both references. *Then* set thresholds from what comes back. Metrics first, gate second — inventing the threshold is the error we just caught.
3. **Re-ask A4** with the sourcing rule attached. "How long before a static frame loses a viewer" is the one question we most need and least have.
4. **C2's five constraints** into the template — the architecture item from the backlog.
5. Leave the parallax clamp to the lane that owns it, with the confirmed defect written down.

## What changes in the brief for the next pass

Add to §2's output contract:

> Every number carries a **retrievable locator** — page or section of the cited work, or
> a URL. A number whose source is a book or paper with no page is a design proposal, and
> must be labelled as one. Proposals are welcome; proposals wearing citations are not.
> The bibliography certifies nothing about the body.
