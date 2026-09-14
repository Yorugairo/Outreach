/* SPACE: stage */
/* species/spotlight.mjs - THE LIGHT (P57 T19 / R26-96; the operator's own species: "the drawn circles should be
   on the layer beneath the card" is the RING's law, and this is the other one - the focus that is not a mark at
   all). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN
   spotlight and KINETICS:END, AFTER trace - it imports nothing, so its place in the order is only a place.

   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the engine's body.
   The last statement registers the painter in SPECIES_PAINTERS; node, where no such registry exists, still
   imports the file for the pure math below. Promoted from inline engine code (`paintSpecies sp.kind ===
   "spotlight"`) with every golden byte-identical: each literal below is the value the inline code carried, to
   the digit (SP.SPOT_DIM and SPOT_R_PORTRAIT among them), and no expression was re-associated.

   WHEN (`SPECIES_WHEN["spotlight"]`, build_scene_timeline_f.py:315, verbatim): "the sentence's focus is a
   PICTURE or a datum and the rest may dim - the light lands on it and holds until the sentence has a reason to
   leave (dur 'hold', E25 amended)".

   THE LAW - E56 (the ring's one use, 2026-09-08): a ring circles a number or a point on a CHART only; A
   PICTURE'S FOCUS IS THE LIGHT. So this species is what points at everything a ring may not, and it points by
   taking light AWAY from the rest of the frame - one dimmed rect over the whole stage with a feathered hole
   punched in it, never an outline, never a shape drawn on the thing itself. E56's second half is why the hole
   is alive: THE LIFE CHECK RUNS ON THE ADDITION'S OWN REGION, so the light itself carries a named idle (E49,
   2026-09-09: "make sure all of the new additions pass the life check with the pixels shifting") - absent, it
   is explicitly still. E25 amended (the operator, 2026-09-08: "right now we flash it on, and really, it should
   hold until it has a reason not to"): `dur: "hold"` is resolved by the COMPILER (build_scene_timeline_f.py
   :4086-4094, to the next event on the row or the row's end, floored by HOLD_MIN_S), so the painter below sees
   plain seconds and carries no opinion about how long a light should hold.

   THE FORM, all of it a pure function of t:
     the dim    ONE rect over the whole stage, filled with a radial gradient of black: transparent out to r0,
                feathered to full DIM over the next FEATHER of the gradient's radius, and DIM from there to the
                edge. Two stops at 0 and r0 (not one) are what make the hole flat-clear rather than a vignette.
     the hole   its radius is the TARGET's own half-width (floored at W_MIN, so a datum - which resolves to a
                point, w = 0 - still gets a pool to sit in) plus PAD, as a fraction of the gradient's radius:
                the landscape half-stage, kept AT R_PORTRAIT in portrait on purpose (the one landscape number
                the portrait pass left alone, 2026-09-08 - a round hole the width of the short side).
     the glide  the centre runs from `target`'s centre to `target2`'s over GLIDE_S on the io ease, starting at
                at + glide_at. No target2 is the same target, so the glide is a stillness, not a special case.
     the idle   the hole's radius breathes by the idle's SCALE and its centre drifts by the idle's OFFSET - the
                same seeded pure-function-of-t kinetics every held thing carries, phased off lpHash so two
                lights in one scene are never in step. Absent, or "none": {scale: 1, dx: 0, dy: 0}, still.
     the fade   the species' own in and out over IN_S at each end of dur, on the cubic ease.
   Nothing is stored: every visual reads from t, k, dur and the seed. The dials below are ours to tune
   (42 s42.5), not findings - DIM is the operator's own (2026-09-03: 0.55 "way too dark", 0.44 too light). */

export const SPOTLIGHT = Object.freeze({
  GLIDE_S: 0.6,       /* the travel between the two declared targets, in seconds [the engine's `/ 0.6`, verbatim] */
  IN_S: 0.4,          /* the species' own fade in - and out, at each end of dur */
  DIM: 0.49,          /* how dark the rest of the frame goes [SP.SPOT_DIM - operator 2026-09-03: 0.55 was "way too dark", 0.44 too light] */
  FEATHER: 0.12,      /* the soft edge, as a fraction of the gradient's radius: clear at r0, full DIM at r0 + this */
  W_MIN: 240,         /* the floor under the target's width, so a DATUM (a point, w = 0) still gets a pool ... */
  PAD: 60,            /* ... and this much stage px of room around whatever the half-width came to */
  R_PORTRAIT: 960,    /* PORTRAIT: the gradient's radius in userSpaceOnUse - half the LANDSCAPE width, kept on purpose (2026-09-08) */
  R_LANDSCAPE: 0.5,   /* landscape: the gradient is in objectBoundingBox units, so its radius is half the box */
  HASH_SALT: 991,     /* the salt the idle's phase is taken with - the light's own stream */
  INK: "#000",        /* the dim is black taken away from the frame, never a colour laid over it */
});

/* THE GLIDE at t: 0 before at + glide_at, 1 from GLIDE_S after it. `io` is handed in (the engine's spIO, which
   clamps) - the same one the inline code used. A species with no glide_at begins gliding at `at`. */
export const spotlightGlide = (t, sp, io, S = SPOTLIGHT) => io((t - sp.at - (sp.glide_at || 0)) / S.GLIDE_S);

/* THE IDLE the row declared, as a transform, or the identity. `idle` is the engine's idleXf and `phase` the
   seeded phase; an undeclared idle and an explicit "none" are the same still light (E49's declared stillness). */
export const spotlightIdle = (sp, t, phase, idle) =>
  (sp.idle && sp.idle !== "none" ? idle(sp.idle, t, phase) : { scale: 1, dx: 0, dy: 0 });

/* THE HOLE'S CENTRE in stage px: between the two targets' centres at g, plus the idle's own drift. */
export const spotlightCentre = (ca, cz, g, ix) =>
  ({ cx: ca.cx + (cz.cx - ca.cx) * g + ix.dx, cy: ca.cy + (cz.cy - ca.cy) * g + ix.dy });

/* THE HOLE'S RADIUS as a fraction of the gradient's own radius: the FIRST target's half-width (floored) plus
   PAD, breathed by the idle's scale. The first target sizes it for the whole glide - a light does not change
   size because it moved. */
export const spotlightRadius = (a, ix, portrait, stageW, S = SPOTLIGHT) =>
  ((Math.max(a.w, S.W_MIN) / 2 + S.PAD) * ix.scale) / (portrait ? S.R_PORTRAIT : stageW / 2);

/* THE GRADIENT's own attributes: userSpaceOnUse in portrait (a round hole, the offsets keeping their landscape
   size), the default objectBoundingBox in landscape, where the centre is a fraction of the stage. */
export const spotlightGradient = (id, cx, cy, portrait, stageW, stageH, S = SPOTLIGHT) =>
  (portrait ? { id, gradientUnits: "userSpaceOnUse", cx: cx.toFixed(1), cy: cy.toFixed(1), r: S.R_PORTRAIT }
            : { id, cx: (cx / stageW).toFixed(4), cy: (cy / stageH).toFixed(4), r: S.R_LANDSCAPE });

/* THE FOUR STOPS, in order: clear at the middle, clear at r0 (the flat hole), DIM at r0 + FEATHER, DIM at the
   edge. Dropping either of the first two turns the light into a vignette. */
export const spotlightStops = (r0, S = SPOTLIGHT) => [
  { offset: 0, "stop-color": S.INK, "stop-opacity": 0 },
  { offset: r0.toFixed(3), "stop-color": S.INK, "stop-opacity": 0 },
  { offset: (r0 + S.FEATHER).toFixed(3), "stop-color": S.INK, "stop-opacity": S.DIM },
  { offset: 1, "stop-color": S.INK, "stop-opacity": S.DIM },
];

/* THE FADE at k: in over IN_S and out over IN_S, on the cubic ease handed in (the engine's spEase). */
export const spotlightFade = (k, dur, ease, S = SPOTLIGHT) =>
  Math.min(ease(k * dur / S.IN_S), ease((1 - k) * dur / S.IN_S));

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the clock,
   the layer already chosen for the kind's target, and the shared helpers by name. */
export function paintSpotlight(ctx) {
  const { sp, k, dur, t, si, seed, svg, el, resolveTarget, centre, ease, io, idle, hash, STAGE_W, STAGE_H, PORTRAIT } = ctx;
  const a = resolveTarget(sp.target), z = resolveTarget(sp.target2) || a;
  if (!a) return;   /* the targeting law: no resolved target, nothing painted */
  const g = spotlightGlide(t, sp, io);
  const ix = spotlightIdle(sp, t, hash(seed | 0, si | 0, SPOTLIGHT.HASH_SALT), idle);
  const { cx, cy } = spotlightCentre(centre(a), centre(z), g, ix);
  const r0 = spotlightRadius(a, ix, PORTRAIT, STAGE_W), id = "spot" + si;
  const defs = el("defs", "", svg);
  const rg = el("radialGradient", "", defs, spotlightGradient(id, cx, cy, PORTRAIT, STAGE_W, STAGE_H));
  spotlightStops(r0).forEach((stop) => el("stop", "", rg, stop));
  el("rect", "", svg, { x: 0, y: 0, width: STAGE_W, height: STAGE_H, fill: "url(#" + id + ")",
                        opacity: spotlightFade(k, dur, ease).toFixed(2) });
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.spotlight = paintSpotlight;
