---
name: visible-difference-and-local-life
description: "E99 s38 (2026-09-15) - a review card is judged only on a VISIBLE difference; plate life comes from the local stack (ambient lane, layered plates), not a pixel drift; and \"no decision for me\" meant \"I can't see it\", not \"not my call\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-16T04:05:38.159Z
---

The drift-plate card (r26-133) asked the operator to judge a 2.3 px Lissajous drift at eight frames per pixel. Their answer:
"no decision for me I don't even notice it while i'm watching" - and when I read that as "the agent's call", the correction:
"i wasn't saying it's not my call to make, i was saying that I can't make a decision on it because it's not realy a visible
shift". Then the direction: "the better way to gain motion isn't to use our local capabilities on the plates to bring life to
them instead of just shifting the pixels like that".

**Why:** a proof with no visible difference has nothing to judge, so the card was the agent's failure, not a ruling; and the
record already held the real answer (CAPABILITIES:142 the mask-pinned AMBIENT lane, :141 the parallax engine, :144/:146 the
layered plate under the camera) - the drift is only E49's floor.

**How to apply:** before serving any look/watch card, read the clip yourself for a visible difference; if none, do not ask.
Never read "no decision for me" as delegation - ask what they could not see. A plate's life is generated locally (the ambient
lane on a life region the plate actually has) or comes from its layers under the camera; a pixel drift is never offered as
"life". Related: [judge-the-frame-not-the-diff](judge-the-frame-not-the-diff.md), [check-rulings-before-asking](check-rulings-before-asking.md), [nothing-ever-goes-truly-still](nothing-ever-goes-truly-still.md),
[no-paid-generators](no-paid-generators.md).
