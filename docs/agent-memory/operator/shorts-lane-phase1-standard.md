---
name: shorts-lane-phase1-standard
description: "The NotebookLM shorts treatment is PHASE 1 — hook + compression + dissolves + per-scene Ken Burns + doc-29 captions in brand tokens + safe-zone. Generated plates and chart overlays (\"make it ours\") were tried on the yen short and rejected."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-13T09:37:11.910Z
---

Operator ruling 2026-09-03, after seeing both cuts of the yen short:
**"make it ours" doesn't work well — the phase 1 treatment is the answer for
this lane.**

Phase 1 = Omni/Veo hook over the first seam · gap compression + 5% ·
dissolves at hard cuts · per-scene Ken Burns 1.00→1.04 alternating direction
· NotebookLM's burnt plates cropped (bottom 16%), full-width picture, brand
cream pad · doc-29 kinetic captions in brand tokens (charcoal ink, coral
keywords, cream stroke, 4–6 words/page, anchor ~64%) · **film reel layer** (operator-added 2026-09-03; see below) · bed · dark outro
(deliberate "one high-tech layer") · SRT sidecar.

Rejected for this lane: replacing NotebookLM scenes with generated plates
(codex claim `yen-scene3-plates-v1` — four good plates, wrong lane) and
dropping real-data chart panels onto the picture. Those belong to the
YouTube layer. Don't re-propose them here.

**Why:** the plates and chart pulled the short toward the YouTube evidence
register; the lane's value is NotebookLM's speed with the brand essence
on top. See [shorts-lane-brand-essence](shorts-lane-brand-essence.md), [notebooklm-omni-opener](notebooklm-omni-opener.md).

## Film reel layer (part of phase 1 from the yen short on)

Adapted from MotionKit "Film Burn Intro" — title and burn removed, the
apparatus kept and run the whole main. Rendered in Remotion as an alpha
layer (`outro/src/FilmFrame.tsx`), composited BEFORE the look so the
sprocket strips ride the gate; captions composited AFTER so they hold
steady. Gated off the outro (the one high-tech layer stays clean).

- Strips charcoal `#25313C`, holes cream `#F4E6C7`, 56px; grain 0.08
  overlay; scratches 0.35 (clean projector, not archive); faint flicker.
- **Gate weave is a controlled wave, never random**: y 1.5px @0.7Hz +
  0.5px @11Hz, x 1.1px @0.45Hz. Operator rejected ±4/±6px per-frame noise
  as "erratic spikes, reads like flickering light". Luminance breathe
  ±1.2% (two slow sines). Mild curve, σ0.6 soften, **24 fps**.
- **No halation on paper** — the screen-blend bloom turned the cream pink.
- Reel audio: Freesound **#241886 "8mm projector sound"** (CC0), from
  20s in, VO window only, faded before the outro. Level: the operator set the reel at -22 under the voice with the music at -26 (2026-09-03, LEDGER 9ec5e721e4a0; an earlier "10 dB under the mix" here was stale - P54 T2).
  Operator wanted the claw *clicking*, not motor whir; #412145 was rejected.
- Delivery details (P54 value pass folds, 2026-09-13): on Facebook the SRT ships as a sidecar named
  `<name>.en_US.srt` (the locale is read from the filename; embedded mov_text is less predictable). Meta's 35% bottom
  band is the EXPANDED-caption worst case - in normal playback the collapsed caption covers ~the bottom 25%; judge the
  safe zone on a phone. The bed resolves after the last word: a hard cap before the bed's scheduled fade left it at
  -37 dB when the voice stopped, then a cut; the bed swells once the VO ends (+8.9 dB) to carry the ending.
- Windows: lane-specific intermediate filenames + one retry in `run()` —
  a just-written mp4 is briefly locked and the next lane's overwrite fails.
