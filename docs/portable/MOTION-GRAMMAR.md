# MOTION GRAMMAR — narration-locked choreography, portable

Model-agnostic, renderer-agnostic (vanilla JS/CSS, GSAP, Remotion —
anything frame-addressable). Reference implementation: the
scene-evidence player's `stackbox`/`drawStack` + doc 29 §9.24–9.24b;
feel reference: the hyperframes-opening-v1 pilot. Extracted
2026-08-30, the Steel and Paper verdict stack.

## The core discovery

**The dance is the focus hand-off, not the entrance.** Elements that
fly in impressively and then sit in a grid read dead within seconds.
What reads as "the evidence is actually dancing":

1. **Word-matched beats** — every element's enter is anchored to a
   verbatim phrase in the narration, never a hard-coded second. On a
   retime, beats re-derive from their phrases.
2. **Focus hand-off** — each element enters LARGE near center-stage
   and owns the frame while its phrase is spoken; when the next
   element's beat lands, it recedes to a small rail position at the
   frame edge, shrinking as it travels. The composition renegotiates
   space on every narration beat.
3. **Motion hierarchy = attention hierarchy** — the active element
   drifts continuously (slow sine wander + scale breathing); railed
   elements settle to near-stillness. The eye always knows which
   proof is speaking.
4. **The clear is rhetoric** — on the argument's pivot line, burst
   everything at once: radial throw along each element's own bearing
   from stage center, 50–60ms stagger, spin + fade ~0.5s. The removal
   lands the turn.
5. **Full-frame, never framed** — elements live over the whole scene,
   background breathing through the gaps. Caging the choreography in
   a panel kills it (operator: "dancing around the world plate, not
   static on the evidence layer").

## The architecture rule (generalizes furthest)

**Every pose is a pure function of the master clock** (the audio
time): `pose(t) = blend(rail_pose, active_pose, ease(enter_beat,
next_beat, t))`. No accumulated timeline state. This buys exact
scrubbing, deterministic frames for review and render, and
clock-portability. Stateful timelines (GSAP-style) can match the look
but lose all three.

Numbers that worked: enter ~0.6–0.9s expo-out from depth with slight
Y-rotation; recede ~1.0s cubic in-out to identity; active pose ≈ 44%
of frame width near center, rails 22–26% at edges; the host window
extends ~1s past the burst so the final frames still tick.

## Content rule

Finale/recap elements are documents the viewer has ALREADY seen with
their sources. The wall re-presents; it never introduces evidence.

## Lifecycle rules

- Stage-mounted layers outlive their host's draw loop — extend the
  host window past the clear, and remove explicitly after the burst
  completes (and on scrub-back before the enter).
- A re-shown document is a RECAP (see CHART-DISCIPLINE.md class 10).
