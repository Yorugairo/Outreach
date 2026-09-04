# What the research bundle already answered — 2026-09-04

I reviewed the answers file (08) and spot-checked the academic monograph (07), then
built a verdict and a response on that basis. **Files 01–06 I flagged as unreviewed and
then never went back to.** The operator caught it. Reading them changes four things and
retracts one of my own claims.

The bundle is not raw material waiting to be processed. It contains primary measurement
we commissioned, and it closes open backlog items.

---

## 1. B5 is answered from our own data — and it kills my hypothesis

`04_shot_ledger_100_cuts.md` is a frame-accurate 100-shot ledger of the reference
episode. I computed the distribution rather than reading the summary:

| | Wealth Logic (reference) | Steel and Paper (ours) |
|---|---|---|
| runtime | 1013.6 s / 16.9 min | 806.5 s / 13.4 min |
| shots | 100 | 75 |
| **cuts per minute** | **5.9** | **5.6** |
| mean shot | 10.1 s | 9.5 s |
| median shot | 9.6 s | 9.7 s |
| **Q1 / Q3** | **6.3 s / 13.2 s** | **7.6 s / 11.0 s** |
| **interquartile range** | **6.9 s** | **3.4 s** |
| longest hold | 26.0 s | 19.1 s |
| shortest | 1.6 s | 1.7 s |
| ≥ 6 s | 80 % | 88 % |

**We cut at the same rate they do.** Mean, median and CPM are within noise. My working
hypothesis — that our 68 % mid-word cut rate comes from cutting too often — **is wrong,
and I retract it.** I also said the transformation architecture would help by reducing
cut count; that reasoning was wrong too. (The architecture is still right, for the E25
continuity reason, not for a cut-budget reason.)

**What actually differs is the spread. Our interquartile range is half theirs.** We hold
the right average with the wrong distribution: we metronome, they vary. A 26-second hold
and a 1.6-second punch inside one episode is a rhythmic instrument we are not playing.

Two consequences:

1. **M13 is a free win.** Since cut *frequency* is already right, landing cuts in gaps
   costs nothing structurally. It is pure placement.
2. **Shot-length variance becomes a target in its own right** — the same lesson as the
   WPM finding, where the means matched and the spread was the story. Here the spread is
   measurable and we are visibly tighter.

## 2. M10 is measuring the wrong thing

Reference first minute: **10.6, 15.6, 6.0, 3.7, 13.5, 3.7, 2.9, 14.9 s.** Five of eight
shots exceed six seconds; three exceed thirteen.

Our M10 says *no still over 6 s in the first minute*. That is only defensible if **still
means "no motion within the shot," not "no shot longer than 6 s."** The reference holds a
single shot for fifteen seconds while material accumulates inside it — which is exactly
what E21 ("the screen is never still") actually asks for.

**If M10 has been enforced as a shot-length ceiling, we have been cutting against the
reference's own practice to satisfy a gate that meant something else.** Worth checking
what the gate actually measures.

This also connects to E1: motion energy per frame is precisely the instrument that
measures stillness-within-a-shot. The right M10 is an E1 metric, not a duration cap.

## 3. Backlog R2 is closed by `01_wealth_logic_production_report.md`

All four of the "unverified Wealth Logic composition claims" are answered, and **R2a —
the one I flagged as the only item that could change script architecture — is confirmed
with its actual content:**

> **The unifying equation spine.** The episode introduces one equation in P1 —
> `Spread = (Rate of Return − Cost of Debt) × Leverage` — and then presents all six
> mechanisms as *the same equation with different variables plugged in*: trade credit
> (cost 0 %, leverage ∞), cash-out refi, buy-borrow-die, SBLOC, 0 % balance transfer,
> credit-score optimisation. **P6 closes by returning to the equation verbatim.**

That is why a six-item listicle does not read as a listicle. It is one mechanism
evaluated six times, with the ring close landing on the mechanism itself. This is
directly transferable and it is a script-architecture finding, not an art-direction one.

Also confirmed: ~10 s evidence holds (10.13 s mean), a single persistent diegetic host,
physicalised metaphor props (balance scale labelled EARNS vs RENT, stamps, a crate of
pens) staged on a quiet ground.

## 4. Backlog R4 is answered by `02_drawing_engine_and_transforms_research.md`

R4 asked whether Flow Characters lock identity under motion; our own test showed hair
drift on a 6-second clip. The bundle's answer is that the question is wrong:

> **Do not generate the character per shot. Build a vector cutout rig with swappable
> slots** (torso / head / hand), driven by forward kinematics and triggered by tags.

Drift goes to zero by construction rather than by better prompting. The document also
supplies the Z-stack the engine should use — Z0 ground, Z1 environment, Z2 interactive
evidence, Z3 host rig, Z4 kinetic overlays, Z5 captions — which is the concrete form of
backlog A6 / C3.

`06_unified_ledger_drawing_engine_and_comfy_spec.md` then carries a `ledger_page.v2.json`
contract built **on our existing LP clock** (roll 0.7 / savor 0.8 / field 2.4), not a
replacement for it. That is the right kind of integration and it should be read before
we write the object-page renderer.

---

## 5. Two discrepancies to settle

**Speech rate.** The reference runs **183.6 WPM**; we measured ep1 at 182.8. Our
doctrine target is **145–165 WPM**. The target is below both our own practice and the
best-performing reference we have. Someone should decide which is right rather than
leaving a gate that neither we nor the reference satisfies.

**The acoustic gap threshold.** File 01 gives the breath-gap rule as **≥ 0.45 s**; file
08 and the M13 proposal use **≥ 0.30 s**. These produce different gate behaviour. Pick
one, from the measurement.

**Parallax dials** (06, more specific than 08): `intensity` 0.08–0.15, hard ceiling
0.18; `steady_value` 0.35–0.45; `edge_fix` 4–6 px; `ssaa` 1.5–2.0; model
`depth_anything_v2_vitl_fp32` with a claim that fp16 is "strictly banned due to logit
underflow." That last is a specific technical assertion and should be tested on one roll
before it becomes a standard — our current file uses `vits_fp16` and has produced usable
output.

## 6. The process note

The bundle's own index (`00_README_INDEX.md`) routes each file to a consumer — 04 to the
editor, 02 to the motion designer, 07 to the engine architect. **I read the file
addressed to me and treated the rest as context.** That is how a research layer gets
commissioned and then half-used.

Rule going in: **a research bundle is read by its index, not by its summary.** The
summary is written by the same pass that wrote the material and inherits its blind
spots; the index tells you what was actually produced.
