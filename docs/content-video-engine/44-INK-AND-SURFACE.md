# 44 — Ink and surface: why vector ink looks sterile, and the three models that fix it

Extracted from `07_academic_literature_drawing_and_2_5d_animation_engine.md` §1.4.
Status: **reference — not yet folded to portable.** This is the physical basis under the
E22 page signature.

---

## 44.1 Alpha blending is the wrong operator (Kubelka–Munk 1931)

**This is a compositing bug, not a taste preference.** Standard
`dst·(1−a) + src·a` models an opaque film over a background. Layered translucent pigment
obeys two-flux radiative transfer:

```
dI/dz = −(K+S)I + SJ
−dJ/dz = −(K+S)J + SI
```

where K is absorption and S scattering. Alpha compositing two ink passes yields a dull
desaturated grey; K–M yields the deepening you get when real ink crosses real ink.

**Where it applies:** anywhere two ink strokes overlap on the page — a chart line
crossing an axis, a callout over a bar, a highlighter over a written figure. Our
highlighter species is the most visible case.

## 44.2 The dark rim (Deegan et al. 1997)

Real sumi and watercolour do not fill uniformly. A pinned droplet perimeter evaporates
fastest at the edge:

```
J(r) ∝ (R − r)^(−λ),        λ = (π − 2θ_c) / (2π − 2θ_c)
v_radial(r) = 1/(ρ r d(r)) · ∫ᵣᴿ J(r′) r′ dr′  > 0
```

Outward flow carries carbon to the perimeter and deposits a **dense dark ring**. A flat
fill is the tell of a vector.

**Where it applies:** the E22 ink field as it reaches the deckle, and any filled inked
prop. The field already stops at the deckle; this says the *edge should be darker than
the interior*, which is the opposite of a soft feather.

## 44.3 The halo (Chu & Tai 2005)

Wicking through kozo fibres obeys Darcy's law for porous media:

```
q = −(K/μ) ∇p
```

with **K an anisotropic permeability tensor aligned to the deckle grain (~22.5°)**. Small
particles diffuse deep into capillary pores producing a pale amber *bokashi* halo; large
carbon aggregates are trapped near the boundary producing a velvety black core.

**Where it applies:** the grain direction is a real, orientable parameter. Ink spreading
should be anisotropic and should agree with the paper's grain across the whole page —
consistency here is what reads as one sheet.

## 44.4 What this does not license

E22 is a **final** operator ruling with an explicit refusal list: blob bleed, gap, coffee
stains, halo, fibre, white ground. §44.2 and §44.3 describe **sub-pixel behaviour at the
ink boundary**, not visible decoration. The dark rim is a one-to-two-pixel edge density
gradient; the anisotropic spread is a directional bias in how the field advances. **If
either becomes visible as an effect, it has violated the ruling and is wrong.**

The operator's refusal of "halo" in E22 was of a *visible glow*. §44.3's *bokashi* is a
sub-pixel amber cast at the ink margin. Ship it only if it cannot be named by eye.

## 44.5 Priority

Below §42.1 and §42.2. This is the finish, not the motion — it raises the ceiling on a
page that already moves correctly, and it is worth nothing on a page that still draws
like a plotter.

## 44.6 Sources

Kubelka & Munk 1931 · Deegan et al. 1997, 2000 · Chu & Tai 2005 · Winkenbach & Salesin
1994. Primary: `07` §1.4. Governing ruling: E22 (final, 2026-09-03).
