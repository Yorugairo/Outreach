---
name: soak-ink-is-a-plate
description: "The ledger page's ink soak: six rounds of Kubelka-Munk filter chains (mesh, grain, creep, step motion) lost to the shipped alpha film's pooling; the operator's ideal is 'we actually paint it with ink' and the cream-to-ink plate fade was 'one of our best variants' - the image model carries the ink, the engine carries the motion"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T12:52:26.103Z
---

**What happened (2026-09-05).** P43 T3 landed Kubelka-Munk on the soak's stains (correct two-flux physics, a rendered probe within 3/255). In motion the operator judged six rounds: the plain K-M ("I do like it, wish it was more erratic"), an attraction mesh ("more wobble, higher grain, less blue"), a boiling field ("looks like a burn-in"), the middle ground, more wobble with a slow creep ("too smooth"), then step motion with jitter and per-stain delays. Verdict: "in a way our original applications were better, with the ink pooling/blotchiness ... the ideal feeling is that we actually paint it with ink. The fade in from cream to the ink surface has still been one of our best variants" -> "turn ink off".

**Why:** carbon under K-M hides almost immediately, so the translucent grey pooling the alpha film had by accident collapses to two tones, and every round after was hand-dialling that pooling back. A filter chain does not make ink; a generated inked plate does (E40: image generation is the strong lane).

**How to apply:** `km_ink` stays a capability for ink OVER ink (a ring over a bar, the highlighter), never for the soak. The soak's next build is a PLATE REVEAL: a generated ink-on-cream plate revealed by the growing stains as a mask, the stepped clock and jitter (`soakStepped`, `soakJitter`) driving the mask, the `field_plate` cross-fade as the end state (BACKLOG 9). When the operator says "more erratic", ask which he means before building: shape (mesh), tone (wash), or time (step motion) - they landed in that order and only the last was the ask. Judge motion in LIVE play from the player's Play button; the in-app pane throttles animation frames while hidden. See [review-server-no-store](review-server-no-store.md), [flow-stills-first-image-to-video](flow-stills-first-image-to-video.md), [ledger-page-signature](ledger-page-signature.md).
