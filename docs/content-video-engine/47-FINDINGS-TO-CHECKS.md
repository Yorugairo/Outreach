# 47 — Findings to checks: what today's research can actually enforce

The TDD discipline applied to doctrine: **for every finding in 42–46, name the check that
would fail without it.** A finding with no nameable check is either not yet specific
enough to be doctrine, or is genuinely a JUDGE row — and it gets labelled that way rather
than sitting in a doc pretending to be a rule.

Three tiers, in order of strength:

| tier | mechanism | why it beats the next one |
|---|---|---|
| **1 · DESIGNED OUT** | the wrong path does not exist in the code | nothing to catch; you cannot draw a stroke wrong if there is no linear mode |
| **2 · GATED** | a mechanical check reads an artifact and FAILs | catches violation after the fact, but catches it every time |
| **2b · AGENT-JUDGED** | a model executes the judgment on every build | reproducible and automatable; belongs with P36, the viewer |
| **3 · JUDGE** | a human reads and verdicts by hand | real, not mechanical, not automatable |

Anything that fits none of the three is **DEMOTED** — recorded as knowledge, not doctrine.

---

## 0. First, a correction: M10 was already right

I claimed in 46 §46.2 and backlog N1 that M10 measures shot length and therefore forces
cuts against the reference's own practice. **That is wrong.**

`gate_motion_density.py:277` computes a still stretch as the gap between **visual
events** — dock entries, badge lights, caption page beats, stage-mode pages, targeted
species firings — not between shots. A 15.6 s shot with a dock entering at +4 s and a
callout at +9 s has no stretch over 6 s and passes M10 cleanly. That is precisely E21's
intent, correctly implemented.

Shot length has its own separate ceiling: `PLATE_HOLD_MAX_S = 20.0`, with an escape when
two docks span the hold. The reference's 15.6 s first-minute shots clear it, and its 26 s
maximum clears it with two docks.

**The system already distinguishes "the screen went still" from "the plate held long."**
I inferred a defect from a FAIL message without reading the implementation. Backlog N1 is
withdrawn; 46 §46.2 is corrected.

What survives from that line of thinking: nothing about M10, and the tail-growing half of
N2 is deprioritised by operator ruling — our retention fails at the front, and a long
hold is a luxury for an audience that already stayed.

---

## 1. DESIGNED OUT — make the wrong thing unrepresentable

| finding | how it is designed out | the test that proves it |
|---|---|---|
| **42.1 curvature-reparameterised stroke** | `drawOn(path, k)` takes no linear mode. There is one draw path and it is curvature-driven. | Draw a path with one sharp corner and one long straight. Assert `v(at max κ) < v(at min κ)`. **A linear implementation fails this.** |
| **42.1 the κ₀ regulariser** | baked into the velocity function, not a caller option | A straight-line path (κ→0) returns finite velocity, no NaN, no divide-by-zero. |
| **42.1 width/ink coupling** | width is derived from `v(s)`, never set independently | `w(at max κ) > w(at min κ)` on the same path. |
| **42.2 closed-form springs** | the analytic evaluator is the only spring API; no integrator exists to call | **The seek test:** evaluate frame N directly, and evaluate frames 0..N in sequence. Assert bit-identical. An iterative spring fails this by construction. |
| **42.3 area-preserving squash** | the squash matrix is built as `R·diag(1+α, 1/(1+α))·R⁻¹` | `det(A(t)) == 1` within float tolerance, for all t and all α. |
| **43.5B ARAP morph** | polar decomposition is inside the morph, not a caller choice | **Morph a shape through >90° of rotation. Assert `det(J(t)) > 0` at every t.** Naive vertex lerp fails; polar decomposition cannot. This is the cleanest failing test in the set. |
| **48.3 DQS skinning** (doc 48) | joints blend on SE(2) geodesics; linear blend skinning is not an option in the rig | Flex a joint through 180° at w=0.5. Assert `det(T_blend) == 1`. **LBS returns the zero matrix here** — the candy-wrapper elbow, as a one-line failing test. |
| **48.5 prop attachment** (doc 48) | attachment is a cached offset matrix; there is no hierarchy-mutation path | Pick up a prop mid-move; assert world position is continuous across the handover frame (no one-frame pop) and that the node's parent never changed. |

These six are the strongest results of the day, because once built they cannot be
violated — there is no gate to route around.

## 2. GATED — mechanical checks against an artifact

Ordered by value. "Fails on" is the pre-finding behaviour the check catches.

| # | check | reads | FAILs on |
|---|---|---|---|
| **G-o** | **Mobile legibility** (50 §50.2). Every rendered text size, multiplied by the portrait scale (390/1920 = 0.203), clears a 12 px floor. | template + timeline | **14 of the template's 16 font sizes today.** 75.2 % of our watch time is a phone, and axis labels currently render at 5 px |
| **G-a** | **Punch does not overlap a build.** A camera scale change and an evidence build may not share a time window. | timeline scenes + dock spans | our current renderer, which zooms while the chart draws — saccadic suppression eats the numbers |
| **G-b** | **Parallax plate eligibility.** A plate whose asset kind is `actor`, `prop`, `evidence` or carries text may not have parallax applied. | shot table + asset registry | applying Depthflow to the ledger page or to @Mike (45 §45.2, the viability matrix) |
| **G-c** | **Parallax dial lint.** `tiling_mode != "mirror"`, `ssaa ≥ 1.5`, `quality ≥ 80`, `intensity ≤ 0.18`, model is ViT-Large. | `parallax-runner.mjs` config | every value we ship today (45 §45.3) |
| **G-d** | **No unanchored transform.** Any scale or rotate without an explicit anchor. | template + timeline | the diagonal-drift class (43 §43.2) |
| **G-e** | **LTX frame count.** `num_frames % 8 == 1`. | ambient job spec | a 120-frame job that silently produces garbage (45 §45.6) |
| **G-g** | **G15 strengthened: the ring closes on the MECHANISM.** The causal claim named in P1 is what P6 returns to — not merely a repeated token. | script + phase map | a close that echoes a *phrase* while the argument has drifted. See §6 for why the "equation spine" framing was wrong. |
| **G-i** | **The eye-line invariant** (48 §48.7). A composited figure's eye height must sit on the plate's horizon, within tolerance. | shot table + plate metadata + actor placement | the "standing in a pit" read — the single most common tell in composited 2.5D |
| **G-j** | **Zero-slip anchoring** (48 §48.7). Any grounded sprite declares `transform-origin: 50% 100%` and binds translation to floor velocity, never an independent tween. | timeline + template | foot slide, and the floor-shear paradox when the actor and floor ride different planes |
| **G-k** | **Solver declared per contact beat** (48 §48.1). A beat that declares contact resolves IK; a free gesture resolves FK. | shot table | a pointing arc flattened into a straight line, or a planted foot that slides |
| **G-l** | **The mobile safe box** (49 §49.1). On a 9:16 timeline, every dock, caption and evidence element sits inside `x ∈ [80,880], y ∈ [280,1340]`. | template CSS + timeline | **our shipped 9:16 dock CSS** — 136 px into the right rail, 152 px too wide |
| **G-m** | **Generative frame-count law** (49 §49.2/§49.3). Wan jobs satisfy `T = 4k+1`; LTX jobs satisfy `N = 8n+1`. | job spec | an 80-frame Wan job or a 120-frame LTX job — both break causal VAE alignment and flash |
| **G-n** | **Generative guidance ceilings** (49). Wan I2V CFG ≤ 4.5, LTX CFG ≤ 4.5, LTX STG declared, Wan text encoder is the **scaled** FP8, Wan VAE unquantized. | job spec | frame burning, edge strobing, NaN black frames, blotchy VAE banding — each a wasted render |
| **G-h** | **Kubelka–Munk compositing.** Two overlapping ink strokes composite darker than `dst(1−a)+src·a` would give. | rendered plate, sampled | alpha blending, which is the wrong operator (44 §44.1) |

**M13** is settled from the reference (46 §46.3, 2026-09-04): **≥ 0.30 s, cut at 0.8 of the gap, mid-word share ≤ 25 %** — neither report's placement was right
(46 §46.3). It is free: our cut rate already matches the reference, so this is placement
only.

**The E1 metrics** (motion energy, centroid of change, saliency, flow coherence) are
gateable **but not yet** — build the measurement, run it over ep1 and both references,
derive thresholds from that. Adopting a guessed threshold is the exact error the metrics
exist to catch.

## 2b. AGENT-JUDGED — reproducible, automatable, not deterministic

A judgment a model executes on every build. Belongs with **P36 (the viewer)** rather than
the mechanical gates: it is a blind read by a stand-in for the audience.

### V-a · The muted-caption judge

*Operator contribution, 2026-09-04. This is not from the research.*

`RULE-abstract-to-concrete` already says: cover the caption; if you can still tell what
claim is being made, the plate is scenery rather than the punch. **I had recorded that as
a human read. It does not have to be.**

| | |
|---|---|
| **reads** | the prior scene rendered **with** captions (for context), then the test scene rendered **with captions removed** |
| **asks** | what claim is this scene making? |
| **PASS** | the stated claim matches the narration's claim for that beat |
| **FAIL** | the model can only describe the scene — *"a desk at dawn"* rather than *"Japan is selling"* |

**The calibration, which is the important half:**

> **If the check needs stronger reasoning than a decent model can manage, the material is
> too complex for the average viewer.**

That makes a FAIL ambiguous in a *useful* way — it means one of two things, and both are
defects worth surfacing:

1. **the plate is scenery** — it illustrates the setting the line was spoken in rather
   than what the line means; or
2. **the argument is too dense** — the beat asks the viewer to carry more inference than
   the visual supports.

A human JUDGE row returns one bit and spends operator attention. This returns a diagnosis
and runs on every build. It is the first check we have that tests the *pairing* of image
to claim rather than either one alone.

## 3. JUDGE — human, not automatable

- **44.2 coffee-ring edge / 44.3 anisotropic wicking.** Un-gateable *by construction*:
  44.4 says if the effect becomes visible it has violated E22 and is wrong. A check for
  "present but not nameable by eye" is a judgment, not a measurement.
- **43.5 morph method A vs B.** The decision rule ("does this morph carry real rotation")
  is a judgment at authoring time; only the *result* (T4's det test) is mechanical.

## 4. DEMOTED — knowledge, not doctrine

Named honestly, because a finding that cannot carry a check should not sit in a doc
looking like a rule.

| finding | why it demotes |
|---|---|
| **42.4 Euler spirals over Béziers** | Real and worth building. But the quality threshold — how much curvature ripple is too much — we do not have, and inventing one repeats today's error. Build it; do not gate it yet. |
| **42.5 all tunables** (`γ`, `λ_w`, `κ_v`, per-material ζ/ω₀, corner dwell) | Explicitly ours to tune. Configuration, never a gate. |
| **A6 secondary-motion ratio (0.22)** | An invented number. The *shape* (secondary lags 2–4 frames, settles faster) is craft; the ratio is not a finding. |
| **A1 timing chart** | Superseded. `M_p = exp(−πζ/√(1−ζ²))` replaces a guessed table with a solvable model — the model is the mechanism, so there is nothing left to gate. |
| **43.4 dirty flags** | A performance optimisation. Correct, but nothing to enforce. |
| **43.7 BBW / dual quaternions** | Deferred until a prop actually needs to bend. Not doctrine until then. |
| **46.1 grow the tail** | Deprioritised by operator ruling 2026-09-04: our retention fails at the front, so a 26 s hold is a luxury for an audience that already stayed. Recorded, not actioned. |

## 6. Two corrections from the operator, 2026-09-04

**G-f is withdrawn — it was not animation doctrine.** I had gated "the actor resolves to a
registered rig, not a generation," reasoning from the forensic proof that *Wealth Logic*
composites its host. That proves what **they** do; it does not prove generation fails, and
the operator has shipped plenty of generations carrying the character without issue.

More importantly it was the **wrong kind of rule for this document.** Whether an actor is
generated or composited is a channel and style decision. This doc governs *animation
handling* — what motion may be applied to what, and how it is computed. Every other gate
here passes that test; G-f smuggled asset provenance in beside them.

The cutout rig stays in 43 §43.6 as a **technique available to us**, with a real advantage
(deterministic posing, no re-roll), and it is a choice, not a rule.

**What this exposes is a genuine hole:** we have no standard for how an actor *moves* in
our register — generated or composited. 42–46 cover strokes, springs, morphs, ink and
plate motion, and say almost nothing about figure motion. Logged as an exploration.

**G-g was mis-generalised from a listicle.** I extracted "the equation spine" from a
reference that happened to be a six-item list, and encoded the list's particular shape —
one equation, six variable substitutions — as though it were the finding.

The operator's reading is correct: what is durable is the **narrative:image ring** — a
mechanism stated early, re-instantiated through the body, and closed on at the end. The
six variants are how a listicle expresses it, not the thing itself.

So G-g is not a new gate. It is **G15 strengthened**: we already check that a ring *token*
appears in P1; the finding is that the close should land on the **causal claim**, not on a
repeated phrase. That applies to any shape of episode.

## 5b. Shipped — P37, 2026-09-04

Every row of §2 now names the script that owns it and the state it landed in. A gate is
*shipped* only when its failing case was demonstrated first (the PRP's rule).

| check | script | state | failing case shown |
|---|---|---|---|
| G-a | `gate_motion_density.py` M14 | **shipped** | punch on a card entrance / a badge reveal FAILs; after the settle PASSes |
| G-b, G-c, G-e, G-m, G-n | `gate_comfy_config.py` | **shipped** | the parallax runner as it shipped: FAIL (5 findings), kept as the test fixture; Wan 80 / LTX 120 frames, CFG 6, unscaled FP8, quantized VAE, actor plate |
| G-d | `lint_template_transforms.py` | **INFO** (ladder) | one anchored + one loose -> one finding; first landing lists 11 unanchored transforms in the template |
| G-g | `gate_opening_structure.py` G15b | **shipped as FAIL** (no grandfathering - operator, 2026-09-04) | token echoed, argument drifted -> FAIL; ep1 as shipped FAILs (the planted sentence carries one stem) - the rewrite's first bar |
| G-i, G-j, G-k | `gate_grounding.py` | **INFO-then-FAIL ladder** | wrong horizon / screen tween / contact without solver each FAIL; nothing declared -> INFO, never a silent PASS |
| G-l | `gate_vertical_safe_box.py` + `test_vertical_safe_box.py` | **shipped, and the defect fixed** (P37 T0) | the pre-T0 9:16 CSS verbatim FAILs: docks 136 px into the rail, dock-2 to y 1780, caption at y 1759 |
| V-a | `judge_muted_caption.py` | **shipped as a CLI, unwired** | scenery and over-dense diagnoses on recorded replies; cadence is the operator's |
| G-h | `kinetics/ink.mjs` + `ink.test.mjs` + `test_kinetics_km_probe.py` (flag `km_ink`) | **shipped flag-off, HUMAN GATE pending** (P43 T3, 2026-09-05) | ink over ink is darker by K-M than by a calibrated film for five inks x five thicknesses; the rendered probe (plus-lighter coverage + per-channel table) reproduces the module within 3/255; a thin charcoal wash goes blue-grey - the operator's call |
| 42.1 stroke | `kinetics/stroke.mjs` + `stroke.test.mjs`; template `drawOn` / `strokeFrac` at six draw sites (flag `curvature_stroke`) | **shipped flag-off, HUMAN GATE pending** (P43 T2, 2026-09-05) | the sliding mask `len*spEase(k)` is FASTER in the corner than on the straight after it; the hand is slower; `v(max k) < v(min k)`, `w(max k) > w(min k)`, a straight path finite, rest at both ends |
| 42.2 spring | `kinetics/spring.mjs` + `spring.test.mjs` (flag `analytic_spring`) | **shipped** (P43 T5, 2026-09-05) | THE SEEK TEST: a semi-implicit Euler spring reaches a different frame N when stepped through different frames; the closed form is bit-identical; peak exactly 1 + Mp at pi/wd; zeta = 1 overshoots zero |
| 42.3 squash | `kinetics/squash.mjs` + `squash.test.mjs`; the vortex via `scaleBy`, the badge pop (flag `area_squash`) | **shipped, ON in the Tokyo short** (P43 T4, 2026-09-05) | `det(A) == 1` within 1e-9 across 48 angles x alpha to 1000; alpha zero at rest, deceleration adds, an acceleration along v does not |
| G-o | — | **deferred**: X0 — render one 9:16 frame at 390 px and read it | — |
| M13 | `measure_cut_gaps.py` (the measurement); the gate lands with the edit pass | **settled**: ≥ 0.30 s, cut at 0.8 of the gap, mid-word ≤ 25 % — from Wealth Logic's 99 cuts through Whisper | ep1 as shipped: 39–42 % mid-word, 52 % in-gap — FAILs on both |

The composed script runner (`run_script_gates.py`) carries G15b by construction - it lives
inside the opening-structure gate it already calls. The timeline gates (M14, G-i/j/k) run
with the motion gate on the build; the config and safe-box gates run on their artifacts.

## 5. The scoreboard

**8 designed out (four of them SHIPPED 2026-09-05 by P43: the stroke, the spring, the squash, and G-h's K-M ink - §5b) · 14 gated (11 shipped or on the ladder, 2 deferred — §5b) · 1 agent-judged (shipped unwired) · 2 JUDGE · 7 demoted, all routed to the backlog.**

*(G-o added from **operator analytics**, not research — 50 §50.2. It is the cheapest gate in the set and it FAILs almost the whole template. Updated after docs 48 and 49. G-l is the highest-value gate in the set: it FAILs code we already ship. See 49 §49.1.)*

*(After doc 48. File 09 added two designed-out items and three gates, and resolved two previously-demoted findings — see 48 §48.9.)*

Roughly a quarter of what we extracted cannot carry a check, and one gate was withdrawn
outright as the wrong kind of rule. Both are worth stating plainly — a pass where
everything converted would mean the conversion was not honest.

**Demoted does not mean dropped.** Each demoted item is routed to the backlog as a build
item, an exploration, or an explicit closure; none of them just vanish.

**Build order.** The six Tier-1 items ship as code plus their own tests; that is where
the value is, because they cannot be violated afterwards. G-a and G-c are the cheapest
gates against defects we ship *today*. G-g touches writing rather than rendering and applies to the
Steel and Paper re-script. **V-a is the one to build first among the judged checks** — it
is the only check we have that tests the image against the claim rather than either alone.
