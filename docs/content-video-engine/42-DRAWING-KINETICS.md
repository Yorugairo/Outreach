# 42 — Drawing kinetics: how a stroke, a settle, and a squash are computed

Extracted from `07_academic_literature_drawing_and_2_5d_animation_engine.md` (Pillars 1
and 3) and `02_drawing_engine_and_transforms_research.md` (§2). Status: **reference —
not yet folded to portable.** Proven items graduate to `docs/portable/`.

This doc replaces guessed timing constants with solvable models. Where a number appears
below it is either derived or marked as ours to tune.

---

## 42.1 The stroke — curvature-reparameterised drawing

**The defect it fixes.** `stroke-dashoffset` interpolated linearly in time is constant
velocity along the path. A human pen is never constant velocity. This is why our
draw-on reads as a sliding mask rather than a hand.

**The law.** Tangential speed couples to path curvature (Viviani & Terzuolo 1982;
Lacquaniti, Terzuolo & Viviani 1983):

```
v = γ · ρ^(1/3) = γ · κ^(−1/3)          ρ = radius of curvature, κ = curvature
A = γ · κ^(2/3)                          angular speed — the "two-thirds" the law is named for
```

Flash & Hogan (1985) showed this falls out of the CNS minimising squared jerk
`C_J = ½∫‖r⃛(t)‖² dt`; the variational solution for rest-to-rest motion is the quintic

```
r(τ) = r₀ + (r₁ − r₀)(10τ³ − 15τ⁴ + 6τ⁵),   τ = t/T
```

which is also the correct profile for **any** rest-to-rest move in the engine — the
page roll, the camera punch — not just strokes.

**The implementation.**

```
κ(s) = |ẋÿ − ẏẍ| / (ẋ² + ẏ²)^(3/2)
v(s) = γ · (|κ(s)| + κ₀)^(−1/3) · ψ(s)
t(s) = ∫₀ˢ dσ / v(σ)          s(t) = t⁻¹(t)  by Newton–Raphson: s ← s − v(s)(t(s) − t)
```

- **`κ₀ = (v_max/γ)^(−3)`** is mandatory. On a straight line κ→0 and raw `κ^(−1/3)`
  diverges. This is the term that makes the law implementable.
- **`ψ(s)`** is an endpoint envelope so strokes start and stop from rest.

**Width and ink density couple to the same profile** — this is nib pooling, and it is
free once velocity is known:

```
w(s)  = w_base · [1 + λ_w (v_max/v(s))^α_w]
ρ(s)  = ρ_base · [1 + λ_ρ (v_max/v(s))^α_ρ]
```

**Corner rule.** Where the interior angle between segments is tight, the profile already
slows the pen; an explicit dwell is optional and is **ours to tune**, not a finding.

**Why this is the first build.** `drawOn(path, k)` in the template is already
object-agnostic — charts, callouts, squiggles and props all route through it. Replacing
one interpolant makes every drawn thing in the engine hand-drawn at once.

## 42.2 The settle — closed-form second-order dynamics

**Why iterative physics is not merely slow but wrong for us.** We render frame-by-frame
by seeking. Euler/Verlet/RK4 must run from t=0, so parallel frame workers diverge and
scrubbing breaks. Every dynamic must satisfy the frame-invariance law
`S_f = F(f/fps)` in O(1).

```
ω₀ = √(k/m)        ζ = c / (2√(mk))        ω_d = ω₀√(1−ζ²)

ζ<1   x(t) = 1 − e^(−ζω₀t)( cos ω_d t + (ζω₀/ω_d) sin ω_d t )
ζ=1   x(t) = 1 − (1 + ω₀t) e^(−ω₀t)
ζ>1   x(t) = 1 − e^(−ζω₀t)( cosh ω_r t + (ζω₀/ω_r) sinh ω_r t ),  ω_r = ω₀√(ζ²−1)
```

**The inverse model — the important line.**

```
peak overshoot   M_p = exp(−πζ / √(1−ζ²))        occurring at   t_p = π/ω_d
```

Choose the overshoot the shot wants, solve for ζ. Choose when it should peak, solve for
ω₀. **This is what retires a guessed anticipation/settle table**: a material is two
numbers, and the frame counts follow from them.

A working evaluator returning position *and* velocity for all three damping regimes is
in `07` §5.3 (`content/video_engine/sources/reference_analyses/complete_research_evidence_bundle/07_academic_literature_drawing_and_2_5d_animation_engine.md`, "5.3 O(1) Seek-Safe Analytic Spring Evaluator"); velocity is needed because §42.3 drives squash from it.

## 42.3 Squash and stretch, area-preserving and motion-driven

```
A(t) = R(θ) · diag(1+α, 1/(1+α)) · R(−θ)          det(A) ≡ 1 by construction
α(t) = κ_v‖v(t)‖ + κ_a · max(0, −v̂(t)·a(t))
```

Stretch along the velocity direction, compress across it, area conserved. **α is driven
by speed and by deceleration**, so squash emerges from the motion rather than being
keyframed per beat. `κ_v` and `κ_a` are ours.

## 42.4 Curve quality — Euler spirals for generated geometry

Cubic Bézier curvature is a degree-3-over-degree-6 rational function: it ripples, throws
parasitic inflections and flat spots. Euler spirals (clothoids) hold `dκ/ds = const`,
giving G² continuity and minimising `E_MVS = ∫(dκ/ds)² ds` (Levien 2009; Moreton &
Séquin 1992).

Applies to geometry the engine **generates** — arrows, balance arms, connectors, axes.
Hand-authored art is unaffected.

## 42.5 What is ours to tune, not a finding

`γ`, `λ_w`, `α_w`, `λ_ρ`, `α_ρ`, `κ_v`, `κ_a`, per-material `ζ`/`ω₀`, and any corner
dwell. These are configuration. **No paper is cited for them.** The models above are the
findings; these are the dials on the models.

## 42.6 Sources

Viviani & Terzuolo 1982 · Lacquaniti, Terzuolo & Viviani 1983 · Flash & Hogan 1985 ·
Harris & Wolpert 1998 · Levien 2009 · Moreton & Séquin 1992 · Witkin & Kass 1988.
Primary: `07` Pillars 1 & 3, `02` §2.
