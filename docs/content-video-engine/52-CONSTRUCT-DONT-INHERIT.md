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

## 52.3 That art is generated, and the prompt is the skill

**Corrected 2026-09-04, same day, after the operator pushed back.** The first version of
this section said *"do not generate stick art - it is vector."* That was wrong, and wrong
in a way I should have caught by looking harder at the reference.

> *"You're one of the people I had try to produce that stick art... you gave me what
> looked damn near like a child making a stick figure in paint, and that's not at all what
> we need."*

**It is not stick art.** The medical-store frame is a pharmacist in a lab coat holding an
inventory clipboard, in front of stocked shelving with individually drawn boxes, with two
more figures at a register. Consistent line weight, real proportions, expressive faces.
**Nothing hand-written as SVG gets close**, and my attempt demonstrated exactly that.

**Two different asset types were conflated in one frame:**

| | what it is | how it is made |
|---|---|---|
| **the icon ring** - liquor store, gas pump, hospital | flat, single-object, nameable | **sourceable.** MIT sets (Phosphor, Tabler) plausibly cover these; recolour to tokens |
| **the hero illustration** - the figure, the scene | polished multi-element illustration | **generated.** The tutorials are right and the skill is prompt craft |

### Why generation works there and kept failing here

Across their three frames - the millionaire, the real-estate agent, the pharmacist -
**those are three different people.** Different faces, different hair. They hold *style*
consistency, not *character* consistency.

**That is the whole difference.** Our identity problem is @Mike being the same person
across a thirteen-minute episode, which is what drove the character binding, the re-rolls
and the cutout-rig argument (43 §43.6). **A listicle has no such constraint** - every item
is a new scene with a new figure, so generation's weakest property is never tested.

They did not solve a problem we could not. They chose a format that does not have it.

### The scope this correction puts on 52.1

The addressable-coordinate-space argument holds - **for evidence-bearing scenes**, where a
chart, callout or badge must sit somewhere specific. That is where an inherited raster
fights you, and it is why E25 exists.

**For an illustrative scene, where the image *is* the message and nothing has to be
placed, an inherited world costs nothing** - there is no address to need.

| scene kind | substrate | why |
|---|---|---|
| **evidence-bearing** - a chart, a callout, a datum-anchored prop | **construct** | the evidence layer needs coordinates |
| **illustrative** - the image is the claim, nothing is docked to it | **generate** | nothing needs an address; prompt craft is the cheap path |

I generalised from the evidence lane to the whole engine. *"Generation is the wrong tool"*
would have quietly killed the cheapest path available.

### The division of labour

**The operator has the prompt technique and I do not** - he has watched the tutorials that
teach this style. The useful split: he brings the prompt pattern; the engine makes it
**repeatable** - a locked prompt template, a style token set, and the existing claim and
contact-sheet review loop, so a series holds together without re-deriving the look each
time.

**A2a therefore splits again:** the icon ring is sourced and recoloured (cheap, an
afternoon); the hero illustrations are generated from a locked template under the normal
review quarantine.

## 52.4 What this demotes

The generative stack keeps a real job, but a smaller one than it was hired for:

| | |
|---|---|
| **was** | how we get a world at all |
| **is** | ambience on continuous environmental plates only (45 §45.2's viability matrix), behind a mask-pinned frozen subject (49 §49.3) |

That is the **retention** category of 51 §51.7 — atmosphere for someone who already chose
the channel. It was never the answer to stillness (51 §51.8), and it is not the substrate
that *evidence* lives on.

**It remains the right tool for an illustrative scene** (§52.3) — where the image is the
claim and nothing is docked to it. Two jobs, and only the evidence one was mis-assigned.

**The generative work is not wasted; it is right-sized.** The Depthflow dials, the LTX
mask-pinning and the Wan frame law are all still correct within that niche, and the niche
is real.

## 52.5 What this promotes

1. **A2a - the icon ring.** Sourced and recoloured, not generated. Cheap.
   **A2a-prime - the hero illustrations.** Generated from a locked prompt template the
   operator supplies, under the normal review quarantine.
2. **A2b — the prop library.** Retention-grade, inked, on the page.
3. **P38 T2 — the curvature stroke**, which is what makes a drawn line read as a hand.
4. **A5 — the hands.** With T2 and A5 together, whiteboard animation exists.

**None of these is a research problem.** All four are build items and three are already
planned.

## 52.6 The honest summary

We spent real effort inheriting worlds because building them was out of reach. For the
**evidence lane** that was the wrong trade and is now correctable: a constructed world is
more controllable, cheaper per reuse, and addressable by the evidence layer, which the
inherited one never was.

**For the illustrative lane it was the right trade and remains so.** Generation is the
correct tool where nothing has to be placed, and the skill there is prompt craft - a
learnable, cheap skill the operator already has and the engine should make repeatable
rather than replace.

**The plates are not wasted either.** 326 of them are a real retention asset (51 §51.7).
They are simply not the substrate the information lives on.

## 52.7 Sources

Operator, 2026-09-04. 42 §42.1 · 43 §43.2, §43.3, §43.6 · 44 · 45 §45.2 · 48 §48.5 ·
49 §49.3 · 51 §51.7, §51.8 · `RULE-the-page-is-the-ground.md` · ruling E25.
