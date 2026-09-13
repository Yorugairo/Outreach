---
name: dip-is-a-world-change
description: "The dip is the natural transition when the WORLD actually changes at a boundary - never a dock's, never into a mount; and a correction from the operator is applied at its own width, not wider"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-13T09:37:15.118Z
---

On 2026-09-12 the operator saw a black flash between two chart pages: the compiler's old default (E47 #3,
2026-09-06) dipped in front of any row that carried a dock, so a mount - which is itself the transition - got a
0.47 s dip painted seconds before the plate actually changed. I read the correction twice too wide (first "cut into
a signature", then "no dip by default at all") before the operator spelled it out: "the dip is supposed to be used
as an actual transition when the scene ACTUALLY changes ... the dip was associated with any DOCK, not the dip being
associated to the scene change. That's 2 very different things ... we don't dip into a mount, because a mount
replaces the need for a 'cold' transition."

**Why:** a default dip in the wrong place paints black over the boundary, and a bad frame under it is never seen -
"that's how we have hidden bad frames that have to be manually detected".

**How to apply:** the rule as shipped (bde8ce9): an authored exit wins; a signature enter (mount, spiral, morph)
cuts; a changed world (`world_key`) dips; the same world cuts; docks decide nothing. And when the operator corrects
a reading, change exactly what they named - re-read their sentence for the noun it binds to (the scene change, not
the dock) before touching a default. Related: [chart-form-rulings-e50-e53](chart-form-rulings-e50-e53.md), [nothing-ever-goes-truly-still](nothing-ever-goes-truly-still.md).

**A tightened take moves the dips (2026-09-12, P54 value pass fold):** every cut, dip, dock and cue is keyed to words,
so a re-timed take re-derives with no row touched - but shrinking dead space pushed a 0.47 s dip centred on the next
onset into the tail of the sentence before it. The fix is a wider authored gap at that one seam, never putting the dead
space back.
