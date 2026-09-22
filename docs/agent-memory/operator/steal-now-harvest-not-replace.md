---
name: steal-now-harvest-not-replace
description: "A ported technique must never replace a mechanism the operator has reviewed and locked - harvest the idea, keep the mechanism (the remotion-ui wipe port ruined the locked wipe, found 2026-09-01)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-02T03:37:32.702Z
---

When "stealing" a technique from an external component (remotion-ui,
hyperframes, a showcase), graft the IDEA onto the existing mechanism.
Never swap the reviewed mechanism for the library's version.

**Why:** On 2026-08-30 (commit dd9e476) I ported remotion-ui's
directional wipe into the scene-evidence player. It replaced the hard
`inset()` edge wipe the operator had reviewed and locked with a feathered
gradient mask plus parallax. On review it read as a two-direction fade,
it flipped the reveal direction, and it mirrored the carried light. I
then spent all of 2026-09-01 chasing "flashes" with symptom patches
before `git log -S` found the port. Operator: *"there was something we
were trying to learn from the remotion component, but definitely
over-stepped and ruined what was good about what we had."*

**How to apply:**
- Before porting, ask: does this change what a REVIEWED shot looks
  like? If yes, it is a proposal, not a change - render preview
  candidates side by side and let the operator pick (existing instinct:
  preview-candidates).
- Extract the transferable idea (a floor rule, an easing constant, a
  reveal-timing rule) and apply it inside our mechanism. The remotion-ui
  ports that survived are exactly this kind: badge floor, tip head,
  deposited dots - all chart-side additions, none replaced a mechanism.
- When a transition/motion regresses, check `git log -S<const>` on the
  template BEFORE patching symptoms. Doctrine in doc 29 s9.15: *a reviewed
  refinement outranks the demo it refined.*

Related: [remotion-ui-registry](remotion-ui-registry.md), [production-standards-universal](production-standards-universal.md)

**The other half of this failure, named 2026-09-22 (E99 s87): the harvest that never happens.** The first rule is
about porting badly; this one is about never porting and keeping the name. Twice in a fortnight: `REMOTION-UI-INTAKE-2026-09-07.md`
triaged **RU-2 badge-stamp** as PRIORITY and named its mechanism exactly (the two-spring offset - a clamped scale
spring landing while a free rotation spring still unwinds - "the weight cue our single-spring landings lack"), and
R26-20 stood HALF from 09-11 with the rotation spring deferred in its own words, "port it when a stamp asks for it";
meanwhile `stamp` in the compiler became the vector map's number-at-a-centroid, and the parent later "proved" a prop
could be a stamp by docking a card that throws and lands - the very landing the triage calls weightless. Same week,
`REMOTION-UI-HARVEST.md` (the operator's 2026-08-31 review) said the line's tip is "One gesture instead of overlapping
animations"; R26-228 built a lead point AND halo AND spark AND bloom AND a per-word walk, and the operator read it on
the frame as "2 different pointers" and "chaos" (s83). **Read the harvest note and the intake triage BEFORE building
anything they name, and port the mechanism, not the look.** The note usually already contains the answer and the
failure mode.
