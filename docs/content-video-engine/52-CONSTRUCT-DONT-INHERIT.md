# 52 — Construct, don't inherit

Operator, 2026-09-04:

> *"The stick figures work because you can build the world you need to convey; I was trying
> to avoid building that world because I didn't have the skill to do it, so I tried to
> inherit it by image generating plates."*

**That is the founding-premise correction, and it explains several of our own rules
retroactively.** Generated plates were never an art choice. They were a *substitute for
the ability to construct*, adopted when that ability did not exist. It now nearly does.

---

## 52.1 The technical form of the intuition

A generated plate has **no addressable coordinate space.**

A diffusion model decided where the desk is, where the light falls, where the negative
space sits. You cannot put a callout on the pillar because you do not know where the
pillar is. You cannot have the toll gate stand exactly where the chart will grow, because
the gate arrived pre-composed inside a raster.

A constructed scene has `M_world = M_parent × M_local` (43 §43.2) and a Z-stack
(43 §43.3). **Every object has an address.** A prop can be placed `at: "datum"` — against
the data — because both exist in one coordinate system.

> **Inherited worlds are rasters you decorate. Constructed worlds are scene graphs you
> address.**

### This is why E25 had to exist

**E25** — *"a chart never survives a plate change"* — reads as a motion rule. It is not.
It is a rule legislating around the fact that **the plate was not addressable**: a chart
docked over a generated plate has no relationship to it, so when the plate changes the
chart is orphaned.

On a constructed page the rule is unnecessary, because the chart *is* the page (that is
`RULE-the-page-is-the-ground`). Several of our rules are scar tissue from inheriting
worlds instead of building them.

## 52.2 Whiteboard animation is not a new capability

The operator's original intent — *a hand drawing to life what the narration is saying* —
is not a thing we need to invent. It is **three planned pieces composed**:

| piece | where | state |
|---|---|---|
| a stroke that reads as drawn by a hand, not plotted | 42 §42.1, curvature reparameterisation | P38 T2 |
| the hand itself, working the surface | 43 §43.6 hand slots + 48 §48.5 reach and grasp; `build-f/ledger-hands.html` is an existing proof | backlog A5 |
| ink that behaves like ink | 44 | deferred, and correctly — it is finish, not motion |

**The thing he wanted at the start is what the current build order produces.** It was
unreachable then because the stroke was a linear `stroke-dashoffset`, which is a plotter.

## 52.3 Do not generate stick art — it is vector

> *"'Bad stick art' is a tough prompt."*

Correct, and the answer is not a better prompt. Generators are tuned toward polish; asking
for deliberate crudeness fights the model, and every roll drifts.

**Icons are vector assets, drawn or sourced once, reused forever.** This is the same
argument as the cutout rig (43 §43.6): identity is preserved by *construction*, not by
prompting. And it is cheaper — large MIT-licensed icon sets already exist (Phosphor,
Tabler and similar), so **A2a is probably a selection-and-recolouring job, not an art
project**: pick a set with a consistent stroke weight, recolour to brand tokens, index it
like the plate library.

An afternoon, not a wave of generations.

## 52.4 What this demotes

The generative stack keeps a real job, but a smaller one than it was hired for:

| | |
|---|---|
| **was** | how we get a world at all |
| **is** | ambience on continuous environmental plates only (45 §45.2's viability matrix), behind a mask-pinned frozen subject (49 §49.3) |

That is the **retention** category of 51 §51.7 — atmosphere for someone who already chose
the channel. It was never the answer to stillness (51 §51.8) and it is not the answer to
world-building either.

**The generative work is not wasted; it is right-sized.** The Depthflow dials, the LTX
mask-pinning and the Wan frame law are all still correct within that niche, and the niche
is real.

## 52.5 What this promotes

1. **A2a — the icon library.** Acquisition-grade, vector, sourced not generated.
2. **A2b — the prop library.** Retention-grade, inked, on the page.
3. **P38 T2 — the curvature stroke**, which is what makes a drawn line read as a hand.
4. **A5 — the hands.** With T2 and A5 together, whiteboard animation exists.

**None of these is a research problem.** All four are build items and three are already
planned.

## 52.6 The honest summary

We spent real effort inheriting worlds because building them was out of reach. That was a
reasonable trade at the time and it is no longer the right one — the ability to construct
is nearly here, and a constructed world is *more* controllable, *cheaper per reuse*, and
*addressable by the evidence layer*, which the inherited one never was.

**The plates are not wasted either.** 326 of them are a real retention asset (51 §51.7).
They are simply not the substrate the information lives on.

## 52.7 Sources

Operator, 2026-09-04. 42 §42.1 · 43 §43.2, §43.3, §43.6 · 44 · 45 §45.2 · 48 §48.5 ·
49 §49.3 · 51 §51.7, §51.8 · `RULE-the-page-is-the-ground.md` · ruling E25.
