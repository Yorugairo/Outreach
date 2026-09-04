# The animation math, and what each piece changes in our code — 2026-09-04

From `07_academic_literature_drawing_and_2_5d_animation_engine.md`, read in full after the
operator pointed out that the extraction so far had been about *pacing* — shot lengths,
cut placement, speech rate — and had said nothing about animation, drawing or
transformation, which is what the brief was for.

The monograph is the animation answer. It is correct, it is cited to real graphics and
motor-control literature, and **it derives the LP clock we already ship** rather than
replacing it: roll 0.7 · savor 0.8 · field 2.4 · punch 0.5 · build 3.0 · focus 7.4. It
explains why each beat is the length it is and supplies the math that should drive it.

---

## 1. Every stroke we draw is wrong in one specific, fixable way

**Now:** `stroke-dashoffset` interpolated linearly in time. Constant velocity along the
path. That is a CNC plotter, and it is why our draw-on reads as a sliding mask.

**The fix, in full:**

```
κ(s) = |ẋÿ − ẏẍ| / (ẋ² + ẏ²)^(3/2)          curvature at arc length s
v(s) = γ · (|κ(s)| + κ₀)^(−1/3) · ψ(s)       two-thirds power law, regularised
t(s) = ∫₀ˢ dσ / v(σ)                         invert to get time from arc length
s(t) = t⁻¹(t)                                Newton–Raphson: s ← s − v(s)(t(s) − t)
```

**`κ₀` is the detail that makes it buildable.** On a straight line κ → 0, so a raw
`κ^(−1/3)` sends velocity to infinity. The cutoff `κ₀ = (v_max/γ)^(−3)` bounds it. `ψ(s)`
is an endpoint envelope so strokes start and stop from rest.

**And the width couples for free:**

```
w(s) = w_base · [1 + λ_w (v_max/v(s))^α_w]
ρ_ink(s) = ρ_base · [1 + λ_ρ (v_max/v(s))^α_ρ]
```

As the pen slows into a corner, the line thickens and the ink darkens. **That is nib
pooling, and it falls out of the same velocity profile** — not a separate effect to author.

**Why this is the highest-value single change in the engine:** `drawOn(path, k)` is
already object-agnostic. Charts, callouts, squiggles and the coming props all route
through it. **Replace one interpolant and every drawn thing in the system becomes
hand-drawn at once.**

## 2. The object → chart transform has a proven-safe formulation

My open worry was that a morph would read as a crossfade or collapse mid-way. There is a
mathematical guarantee against the collapse half.

Per triangle, Jacobian `J = D'D⁻¹`. Polar-decompose `J = R·S` — closed form in 2D, no
library:

```
θ = atan2(j₂₁ − j₁₂, j₁₁ + j₂₂)
R = [[cos θ, −sin θ], [sin θ, cos θ]]
S = Rᵀ J
```

Interpolate rotation on SO(2) and stretch on the Riemannian manifold Sym⁺(2), then

```
det(J(t)) = det(R(t))·det(S(t)) = 1 · (λ₁λ₂)^t > 0   for all t ∈ [0,1]
```

Because the principal stretches are positive, **triangle inversion and area collapse are
impossible, not merely unlikely.** Naive vertex lerp collapses whenever rotation exceeds
90°; this cannot.

The global conforming step (ARAP, Sorkine & Alexa 2007) minimises over 1-ring
neighbourhoods with cotangent weights. The Laplacian depends only on rest geometry, so it
factors **once** by sparse Cholesky and each frame is an O(|V|) back-substitution.

**This is what turns "everything transforms out of the chart plate" from an aspiration
into a build.**

## 3. Closed-form springs — and the inverse model I said we didn't have

For a seek-based renderer, iterative integrators are not slow, they are **broken**: Euler
or Verlet must run from t=0, so parallel frame workers drift apart. Every dynamic in our
engine has to be analytic.

```
underdamped (ζ<1):   x(t) = 1 − e^(−ζω₀t)(cos ω_d t + (ζω₀/ω_d) sin ω_d t),  ω_d = ω₀√(1−ζ²)
critical  (ζ=1):     x(t) = 1 − (1 + ω₀t) e^(−ω₀t)
overdamped (ζ>1):    x(t) = 1 − e^(−ζω₀t)(cosh ω_r t + (ζω₀/ω_r) sinh ω_r t)
```

And the line that matters most:

```
peak overshoot  M_p = exp(−πζ / √(1−ζ²))     at   t_p = π/ω_d
```

**That is the inverse model.** In the brief I wrote that I can go parameters → motion but
not desired-perception → parameters, and that an animator's craft *is* that lookup table.
This formula is the lookup table, in closed form: choose the overshoot you want, solve for
ζ; choose when it should peak, solve for ω₀.

**It retires the invented A1 timing chart.** We do not need guessed anticipation and
settle numbers per mass class — we need a material's ζ and ω₀, and the frames follow.
Every "feels heavy / feels snappy" judgment becomes two numbers we can tune and reuse.

## 4. Squash and stretch that preserves area, driven by motion

```
A(t) = R(θ) · diag(1+α, 1/(1+α)) · R(−θ)        det(A) ≡ 1 by construction
α(t) = κ_v‖v(t)‖ + κ_a max(0, −v̂(t)·a(t))
```

Stretch along the velocity direction, compress across it, area conserved. And α is driven
by **speed and deceleration**, so squash emerges from the motion rather than being
keyframed per beat.

## 5. Euler spirals over cubic Béziers for anything we generate

Cubic Bézier curvature is a degree-3-over-degree-6 rational function — it ripples, throws
parasitic inflections and flat spots. Euler spirals hold `dκ/ds = const`, giving G²
continuity and minimising the variation functional ∫(dκ/ds)² ds.

Applies to what the engine *generates*: arrows, balance arms, connector paths, axes.
Hand-authored art is unaffected.

## 6. Why our ink looks sterile — three stacked models

- **Coffee ring (Deegan 1997).** Evaporative flux diverges at a pinned perimeter,
  `J(r) ∝ (R−r)^(−λ)`, dragging carbon outward. Real ink has a **dark crisp rim, not a
  uniform fill.**
- **Anisotropic Darcy flow (Chu & Tai 2005).** Wicking through kozo fibres with a
  permeability tensor aligned to the deckle grain (~22.5°): small particles diffuse deep
  into the pores as a pale *bokashi* halo, large carbon aggregates are trapped at the
  boundary as a velvety core.
- **Kubelka–Munk (1931).** This one is a **compositing bug, not an aesthetic**. Layered
  translucent pigment obeys two-flux radiative transfer. Standard alpha blending —
  `dst·(1−a) + src·a` — is the wrong operator and yields dull desaturated greys. Our
  overlapping ink should composite by K–M.

## 7. Two things we are actively doing wrong, from Pillar 4

**We zoom while the chart builds.** Saccadic suppression during a camera move blinds the
viewer to data updates. The monograph serialises them — punch 3.9→4.4 s, build
4.4→7.4 s — precisely so the numbers land on a still camera. Our LP clock already has the
beats in that order; the renderer needs to honour the boundary rather than overlap them.

**Kinetic type should pop on syllables, not words.** Auditory cortex tracks the speech
envelope in the theta band, 4–8 Hz, ~150–250 ms per syllable. STAGE mode currently keys to
words. Syllable-locked type is phase-locked to the thing the listener's cortex is already
tracking.

## 8. The LP clock is validated, not replaced

The master 6-beat timeline in §5.1 is our clock exactly — 0.7 / 0.8 / 2.4 / 0.5 / 3.0,
focus at 7.4. E22 was derived by eye and by operator correction; the monograph arrives at
the same numbers from the Apprehension Principle and minimum-jerk transitions. That is the
strongest validation the page signature has had.

---

## Build order

| # | change | where | why first |
|---|---|---|---|
| **1** | **Curvature-reparameterised stroke + coupled width** | `drawOn()` in the template | One function. Every drawn object in the engine inherits it. Fully sourced. |
| **2** | **Analytic spring evaluator** (3 damping cases + M_p inverse) | shared timing module | Replaces guessed timing constants with a solvable model; unblocks A1, A3, A6 at once. |
| 3 | **Serialise punch and build** | LP clock in the renderer | A defect we are shipping today, and the fix is a boundary, not new code. |
| 4 | **Polar-decomposition morph** | new, for the `object` page | Makes the transformation architecture real (backlog A3). |
| 5 | K–M compositing for overlapping ink | ink layer | The "sterile vector" complaint, at its root. |
| 6 | Euler-spiral generator for procedural curves | shape helpers | Quality floor for anything the engine draws itself. |
| 7 | Syllable-locked STAGE type | caption layer | Needs a syllabifier on the word timeline. |

Items 1 and 2 are the ones that change how everything looks. The rest are specific fixes.
