# 43 — The scene graph, transforms, and the object→chart morph

Extracted from `02_drawing_engine_and_transforms_research.md` (§1, §3, §4) and
`07_academic_literature_drawing_and_2_5d_animation_engine.md` (Pillar 2). Status:
**reference — not yet folded to portable.**

This is the architecture answer to the operator's question *"because it was all based on
chart drawing, should we be able to link all our objects and manipulate them in relation
just like a chart?"* — yes, and this is the vocabulary that does it.

---

## 43.1 Retained mode, and why we are already right

Immediate mode (raw Canvas/WebGL) issues draw calls per frame with no persistent object
model — fine for particles, hopeless for declarative timing, morphing and lifecycle.
**Retained mode** keeps a scene-graph tree and flattens it to a display list. Our
SVG/template approach is already retained; this doc is about using it properly.

## 43.2 The anchor sandwich — the single most common defect

```
p_screen = M_camera × M_world × p_local

M = ⎡ a  c  e ⎤     a,d = scale · b,c = rotation/shear · e,f = translation
    ⎢ b  d  f ⎥
    ⎣ 0  0  1 ⎦

M_local = T(aₓ,a_y) × R(θ) × S(sₓ,s_y) × T(−aₓ,−a_y)
```

**Without the sandwich, scaling drifts diagonally and rotating an arm disconnects the
hand from the wrist.** Every transform in the engine takes an explicit anchor. This is
the concrete fix for backlog A6 — a prop positioned `at: "datum"` needs its own anchor,
not the stage origin.

## 43.3 The Z-stack

```
Z0 ground (cream page / baseline)      Z3 host rig
Z1 environment (desk, wall props)      Z4 kinetic overlays (stamps, badges)
Z2 evidence (charts, inked props)      Z5 captions
```

Painter's algorithm, strictly back-to-front. Depth cue without 3D:

```
X_proj = X·f/(Z+d) + Cₓ        Y_proj = Y·f/(Z+d) + C_y
```

Assign background props Z=200, evidence dock Z=50, host Z=0, then a small camera drift
produces parallax with no shader at all. **This is the safe way to get depth on a page
that §45 forbids Depthflow on.**

## 43.4 Dirty flags

Each node holds `localMatrix`, `worldMatrix`, `isDirty`. A property change marks the node
dirty and propagates to descendants; the render pass recomputes only dirty subtrees
(`M_world^child = M_world^parent × M_local^child`). Matters at our node counts once props
compose.

## 43.5 The morph — two methods, and when each applies

**Method A — vertex-based (Flubber / d3-interpolate-path), from `02` §2.3.** Cheap,
already-available, right for closed outline shapes:

1. Ring-normalise into exterior rings and holes.
2. Resample both shapes to identical vertex count N.
3. **Rotational alignment:** `argmin_k Σᵢ ‖v_{A,i} − v_{B,(i+k) mod N}‖²` — this is the
   step that stops the path twisting inside-out.
4. Reconstruct cubic Béziers per frame.

**Method B — triangle-based ARAP (`07` Pillar 2).** Needed when the morph carries
rotation past 90°, where naive vertex lerp collapses to zero area.

Per triangle, Jacobian `J = D′D⁻¹`, polar-decomposed — **closed form in 2D, no library:**

```
θ = atan2(j₂₁ − j₁₂,  j₁₁ + j₂₂)
R = [[cos θ, −sin θ], [sin θ, cos θ]]        S = Rᵀ J
```

Interpolate `R` on SO(2) and `S` on the Riemannian manifold Sym⁺(2). Then

```
det(J(t)) = det(R(t))·det(S(t)) = 1 · (λ₁λ₂)^t > 0     ∀ t ∈ [0,1]
```

Principal stretches are positive, so **triangle inversion and area collapse are
impossible**, not merely unlikely. Global conformance uses ARAP local/global with
cotangent weights `c_ij = ½(cot α_ij + cot β_ij)`; the Laplacian depends only on rest
geometry so it factors **once** by sparse Cholesky, leaving an O(|V|) back-substitution
per frame.

**Decision rule.** Outline-to-outline with modest rotation → Method A. Anything where the
prop deforms into a chart with real rotation → Method B. Start on A for the first
`object → chart` page; escalate when a shape actually collapses.

## 43.6 The host is a cutout rig, not a generation

**Forensic proof, from the dossier §3:** frame_0020 of the reference carries three
radically different illustration styles on one canvas — thin-line anime, thick-line
retro-cartoon, flat pastel editorial. A diffusion model renders one style. **That proves
the reference composites independent vector assets.** Repeated identical torso/feet
geometry across frame_0001 and frame_0080 with only the hand swapped proves a pose pack.

```
HandSlot ∈ {point_up, point_side, open_presenting, grip_tool, flat_desk, stop_palm}
HeadSlot ∈ {neutral_talk, explaining_smile, skeptical_frown, focused_down}
TorsoSlot ∈ {standing_labcoat, seated_desk}
```

**1 torso × 3 heads × 6 hands = 18 presenter actions from ~10 transparent files.** Driven
by forward kinematics and switched by storyboard tags, which we already emit.

This closes backlog R4: character drift is not a prompting problem, it is an
architecture choice. Skeletal mesh deformation is explicitly wrong here — it reads rubbery
and erodes the register.

## 43.7 Bounded biharmonic weights and 2D dual quaternions

For props that must bend rather than pivot: BBW (Jacobson et al. 2011) gives C¹
deformation weights with no harmonic creasing, and 2D dual-quaternion skinning on SE(2)
preserves volume where linear blend skinning pinches. **Defer until a prop needs it** —
the cutout rig covers the host.

## 43.8 Sources

Alexa, Cohen-Or & Levin 2000 · Sorkine & Alexa 2007 · Igarashi, Moscovich & Hughes 2005 ·
Jacobson et al. 2011 · Hertzmann & Zorin 2000. Primary: `02` §1/§3/§4, `07` Pillar 2,
`MASTER_RESEARCH_AND_EVIDENCE_DOSSIER.md` §3.
