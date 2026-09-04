# 48 — The figure and the ground: actor motion, object handling, grounding

Extracted from `09_2d_and_2_5d_body_animation_object_handling_and_grounding.md`.
Status: **reference — not yet folded to portable.**

**This closes X10**, the hole exposed when G-f was withdrawn: we had argued about how the
actor is *made* and never written down how it should *move*. Docs 42–46 cover strokes,
springs, morphs, ink and plate motion and say almost nothing about a figure.

Its bibliography is clean — 20 citations with DOIs, split into biomechanics/mathematics
and craft doctrine, and the ones checkable from memory are correct. The pass-2 sourcing
contract held.

---

## 48.1 The FK/IK boundary — the most useful rule in the document

Two laws, and they are exclusive:

| law | applies to | solver |
|---|---|---|
| **The arc law** (Disney principle 7) | free gestures — pointing, sweeping, waving, head nods | **FK.** A limb rotating under muscle torque traces arcs. Interpolating an IK *target* linearly flattens the arc into a straight line and pops the elbow. |
| **The contact law** | the instant an extremity meets something fixed — a planted foot, a palm on the desk, fingers on a prop | **IK.** Anything else slides. |

Handover blends over ~100–150 ms on the same minimum-jerk quintic
`α(τ) = 10τ³ − 15τ⁴ + 6τ⁵`. On IK→FK the FK angles are matched instantly at the release
frame so momentum carries into the arc.

**Why it matters here:** it is the first rule we have that says *which solver a beat
needs*, and it is decidable from the shot table — a beat either declares contact or it
does not.

**2-bone IK is closed form** (law of cosines, `O(1)`, no iteration, no convergence
jitter) and covers every human limb. FABRIK (`O(N)`, 2–3 iterations) is for spines and
trailing chains. We need the first; the second is deferred.

## 48.2 Balance — why a gesturing figure must move its hips

`XCOM = r_COM + v_COM/ω₀`, `ω₀ = √(g/l)` (Hof, Gazendam & Sinke 2005). Static COM is
insufficient during a gesture, because momentum carries the body outside the base of
support even when the instantaneous COM is inside it.

Two strategies, selected by gesture speed:

- **Ankle** (small, slow): the body sways back as a rigid inverted pendulum.
- **Hip** (rapid, or reaching across a desk): **the pelvis translates posteriorly in
  anti-phase to the arm**, `Δx_pelvis ≈ −m_arm·Δx_arm / (m_pelvis + m_legs)`.

**The failure this names:** a host who points at a chart with only the arm moving. The
counter-balance fold at the hip is what makes a gesture read as a body rather than a
cutout with a hinged limb — and it is exactly the defect a slot-swap rig produces when
the torso slot never changes.

An APA fires **100–250 ms before** a foot unweights, with the centre of pressure shifting
laterally *toward* the swing foot first. Lifting a foot without it is the "anti-gravity
puppet" read.

## 48.3 The rig — why linear blend skinning collapses

SO(2) is not a linear subspace. Blending rotation matrices linearly gives
`det(R_blend) < 1`; at Δθ = 180° with w = 0.5 the matrix is **zero** and the joint
collapses to a paper-thin crease. That is the candy-wrapper elbow.

- **2D dual-quaternion skinning** (Kavan et al. 2008) blends along geodesics in SE(2), so
  `det(T_blend) ≡ 1` at every angle. Volume is preserved by construction.
- **Bounded biharmonic weights** (Jacobson et al. 2011) solve `Δ²w = 0` under box
  constraints, killing the weight bleed that webs adjacent limbs together.

**This changes a deferral.** Backlog D5 held BBW/DQS until "a prop needs to bend." That
trigger is wrong — the moment we rig a *figure*, elbows and knees need it. D5's trigger
becomes the rig, not a prop.

## 48.4 Idling — the "alive" answer, for a figure

Doc 42's A4 came back empty on how long a *frame* can hold. This answers the narrower and
more useful question: what a standing figure does when nothing is happening.

- **Breath: 0.20–0.30 Hz** (12–18 /min), and **never a sine** — inspiratory:expiratory
  runs 1:1.5 to 1:2, with a post-expiratory pause of 0.5–1.0 s. Clavicles lift 1.5–3.0 mm;
  the thoracic spine extends 1.0–1.5°.
- **Postural sway** is two-regime fractional Brownian motion — open-loop drift under 1 s,
  closed-loop correction over it. Spectral peak 0.10–0.35 Hz. Head excursion ±5–12 mm
  A-P, ±2–5 mm M-L. Generate from **two pink-noise oscillators at 0.15 and 0.25 Hz** so it
  never loops visibly.
- **Contrapposto**: stance hip **up 4–7°**, shoulder girdle **down 3–5°**, head level at
  0°. Williams' law: *never draw hips and shoulders parallel unless the character is a
  robot.*

The asymmetric breath and the non-looping sway are the two details that separate an "idle
cycle" from alive.

## 48.5 Reach and grasp

- **Transport** follows the same minimum-jerk quintic as everything else in 42 §42.1 —
  peak velocity at exactly τ = 0.50, `v_max = 1.875·v̄`.
- **Grasp runs on its own channel** (Jeannerod 1984): the aperture opens *past* the
  object, `MGA = d + 20–40 mm`, peaking at **τ ≈ 0.68** — synchronised with peak wrist
  *deceleration*, not with contact. The fingers then close over the final 30 %.
- **Re-parenting is a cached matrix, never a hierarchy mutation.** At pickup,
  `M_offset = M_hand⁻¹(t*) · M_world,prop(t*)`; while held,
  `M_world,prop(t) = M_hand(t) · M_offset`. On release the prop inherits
  `v_hand + ω_hand × r_offset`.

That last one is the practical core: **no DOM reparenting, no layout reflow, no one-frame
pop** — and it is `O(1)` and seek-safe like everything else in 42.

The Feix/Cutkosky mapping gives a grasp per prop kind (pen → writing tripod #20; document
→ tip pinch #24; board → lateral pinch #16). Useful as a **slot vocabulary for hands**,
which is what 43 §43.6's `HandSlot` enumeration needs to be filled with.

## 48.6 Mass is communicated before the object moves

- **APA**: for a heavy prop, postural muscles fire **100–150 ms before lift-off** and the
  trunk pulls back ~2°.
- **Grip–load coupling** (Johansson & Westling): `F_G ≥ F_L / 2μ`, so a heavy object gets
  an isometric loading phase — **fingers clamp and flesh squashes for 6–10 frames before
  the prop moves a single pixel.**
- **The unloading dip**: tendon elasticity gives 1–2 frames of *downward* deflection at
  the moment lift begins.

> **Weight is sold before the lift, not during it.** Every one of these is pre-motion.

**Placement** is our existing damped oscillator with ζ by material: heavy rigid ≈ 0.85
(no bounce, 1–3 px compression), medium ≈ 0.60 (one 5–8 % overshoot, settling in 8–12
frames), light metallic ≈ 0.35 (2–3 decaying cycles).

**This resolves backlog D3.** The secondary-motion budget does not need an invented 0.22
energy ratio — §2.8 gives the phase lag analytically,
`φ = arctan(2ζ(ω_d/ω₀) / (1 − (ω_d/ω₀)²))`, on the same
`M_p = exp(−πζ/√(1−ζ²))` we already adopted. **One spring evaluator now serves settle,
secondary motion, and placement.**

## 48.7 Grounding — why composited figures look pasted

Four defects, each with a fix:

1. **Foot slide.** Zero-slip requires `v_contact − v_surface = 0` during contact. Sprites
   anchor at `transform-origin: 50% 100%` and bind translation to the ground homography,
   **never to an independent screen-space tween**.
2. **The floor-shear paradox.** If the floor rides a `far` plane at 1.00× and the actor
   rides `cast` at 1.25×, the feet shear across the floorboards at 0.25×v. Fix:
   `v_sprite(t) ≡ v_floor(y_baseline, t)`, interpolating 1.00× at the horizon to ~1.40× at
   the bottom margin.
3. **The floating sticker.** A single blurred ellipse is the tell. The real thing is **two
   components**: a tight **AO contact slit** (1–4 px, α 0.80–0.95, `#141B22`,
   σ ≈ 0.5–1.2 px, *zero offset*) plus a **directional cast shadow** whose penumbra widens
   with distance from the base, `σ(y) = σ₀ + k(y_base − y)`.
4. **The pit.** **The Norling eye-line theorem**: with a level camera at eye height, the
   horizon passes through the eyes of *every* standing figure regardless of depth. If the
   plate's vanishing lines converge at y = 0.50 and the actor is composited with eyes at
   y = 0.30, the viewer reads them as leaning back or standing in a hole. **The horizon is
   the invariant anchor across every composited layer.**

## 48.8 Harmonisation, in our own tokens

The document integrates with E22 rather than around it:

- **Koschmieder attenuation** drifts background contrast toward the cream ground
  **`#F4E6C7`** — our token — while the host keeps full saturation. A 2:1
  rendering-weight hierarchy.
- **Light wrap**: bleed 4–12 px of blurred background into the sprite perimeter.
- **Substrate grain**: modulate vector fills with washi noise,
  `C = C_vector · [1 + κ(T_washi − 0.5)]`, κ ≈ 0.12–0.16, and stroke in charcoal
  **`#25313C`** rather than pure black, with a 0.6–0.8 px alpha feather.

That last line is E22's charcoal, arrived at independently.

## 48.9 What this changes

| | |
|---|---|
| **closes** | backlog **X10** — actor motion now has a written standard |
| **retriggers** | **D5** (BBW/DQS): the trigger is rigging a figure, not a bending prop |
| **resolves** | **D3** (secondary-motion ratio): ζ and the phase-lag formula replace the invented 0.22 |
| **unifies** | one analytic spring evaluator now serves settle, secondary motion **and** placement — 42 §42.2 gains a third caller |
| **fills** | 43 §43.6's `HandSlot` vocabulary, from the Feix mapping |
| **confirms** | the minimum-jerk quintic is a shared primitive — rest-to-rest moves (07), reaching (09), and FK/IK handover all use it |

## 48.10 Sources

Hof, Gazendam & Sinke 2005 · Horak & Nashner 1986 · Aristidou & Lasenby 2011 ·
Flash & Hogan 1985 · Feix et al. 2016 · Cutkosky 1989 · Jeannerod 1984 ·
Jacobson et al. 2011 · Kavan et al. 2008 · Winter 2009 · Bouisset & Do 2008 ·
Johansson & Flanagan 2009 · Blinn 1988 · Hartley & Zisserman 2004 ·
Kovar, Schreiner & Gleicher 2002 · Koschmieder 1924 · Williams 2001 ·
Thomas & Johnston 1981 · Blair 1994 · Brinkmann 2008 · Wright 2017.
Primary: `09` whole.
