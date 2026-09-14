/* SPACE: stage */
/* species/callout.mjs - THE HAND'S RING ROUND A NUMBER (P57 T17 / R26-97; doc 29 s9.27 "Scribble callout",
   the hw-callout-circle harvest; the underline form is P50 T3's one exception).
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN callout
   and KINETICS:END, AFTER press - it imports underlineFrac from it, and the import order IS the region order.

   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the engine's body.
   The last statement registers the painter in SPECIES_PAINTERS; node, where no such registry exists, still
   imports the file for the pure math below. Promoted from inline engine code (`paintSpecies sp.kind ===
   "callout"` + `calloutPath`) with every golden byte-identical: each literal below is the value the inline
   code carried, to the digit, and no expression was re-associated.

   WHEN (`SPECIES_WHEN["callout"]`, build_scene_timeline_f.py:313, verbatim): "the sentence names a NUMBER or a
   POINT on a chart to ring (E56: a ring's one use); the label is the sentence's figure".

   THE LAW - E56 (the operator, 2026-09-09; docs/portable/OPERATOR-RULINGS.md): A RING CIRCLES A NUMBER OR A
   POINT ON A CHART; a picture's focus is a LIGHT. Nothing here widens that: the USE is enforced where it always
   was, in the compiler (`_validate_callout`, which refuses a ring on a card and a label with no digit in it).
   The one exception is P50 T3's: an UNDERLINE under a QUOTED PHRASE on a press card, declared `form:
   "underline"` on a `phrase` target - the squiggle law (s9.27), the same hand and the same .sq stroke, on the
   underline's own clock (species/press.mjs underlineFrac, over the engine's SQUIG_DRAW).

   THE FORM, all of it a pure function of t:
     the circle - a WOBBLED ellipse round the resolved target: rx = w/2 + RX_PAD + pad, ry = h/2 + RY_PAD + pad,
                  SEGMENTS chords from -START_A half-turns through SWEEP half-turns (past 2, so the hand closes
                  over its own start), every vertex's radius jittered by JITTER off the seeded hash - never
                  Math.random. It draws on by dash-offset over DRAW_S.
     the label  - LABEL_AT into the draw, the sentence's figure pops from LABEL_FROM to 1 on the cubic ease over
                  LABEL_POP_S, written LABEL_DX right of the box's right edge and LABEL_DY above its top (a pad
                  pushes it up by PAD_DY_K of itself), scaled about its own anchor by the row's `label_scale`
                  (opt-in, 2026-09-08: a stamp on a plate reads at phone size).
   Nothing is stored: every visual reads from k, dur and the seed, so a scrubbed frame is the played frame. The
   dials below are ours to tune (42 s42.5), not findings. */
import { underlineFrac } from "./press.mjs";

export const CALLOUT = Object.freeze({
  DRAW_S: 0.7,        /* the whole ellipse's draw, in seconds [the engine's SP.CALLOUT_DRAW, verbatim] */
  RX_PAD: 22,         /* the ellipse's half-width over the target's own box ... [calloutPath, verbatim] */
  RY_PAD: 18,         /* ... and its half-height - the pads species/ring.mjs rings the same datum at */
  SEGMENTS: 28,       /* the chords the ellipse is drawn as: a hand's line, not an <ellipse> */
  START_A: 0.6,       /* the nib starts this many half-turns BEFORE 0 (the expression negates it): up and left */
  SWEEP: 2.08,        /* ... and runs this many half-turns: past the full turn, so the ring closes over itself */
  JITTER: 0.12,       /* each vertex's radius wobbles +/- half of this, off the seeded hash (never random) */
  HASH_SALT: 21,      /* the salt the jitter's hash is taken with - the callout's own stream */
  LABEL_AT: 0.8,      /* the label appears this far into DRAW_S ... */
  LABEL_POP_S: 0.25,  /* ... and pops over this long, on the cubic ease */
  LABEL_FROM: 0.7,    /* the pop's scale from ... */
  LABEL_SPAN: 0.3,    /* ... and how much it adds (never a pop out of nothing) */
  LABEL_DX: 34,       /* the label's x off the target box's RIGHT edge (the pad pushes it out too) ... */
  LABEL_DY: -10,      /* ... and its y off the box's TOP edge: above the ring, clear of the number */
  PAD_DY_K: 0.4,      /* ... which a pad lifts by this much of itself */
});

/* THE PAD the row asked the hand to ring at: a datum resolves to a POINT, and `pad` is how wide the ring is
   drawn round it (the fifth watch). Absent or not a number: none. */
export const calloutPad = (v) => (Number.isFinite(+v) ? +v : 0);

/* THE ELLIPSE as a path, in stage px: SEGMENTS chords round the box's centre, each vertex's radius wobbled by
   the seeded `hash` (seed, i, HASH_SALT) -> [0, 1). `hash` is handed in - the engine's lpHash in the player,
   a stub under node - because the jitter's only source is that one pure hash (handwriting-text rule 2). */
export const calloutPath = (b, seed, pad, hash, C = CALLOUT) => {
  const pd = calloutPad(pad);
  const cx = b.x + b.w / 2, cy = b.y + b.h / 2, rx = b.w / 2 + C.RX_PAD + pd, ry = b.h / 2 + C.RY_PAD + pd, n = C.SEGMENTS, pts = [];
  for (let i = 0; i <= n; i++) { const a = -Math.PI * C.START_A + i / n * Math.PI * C.SWEEP; const j = 1 + (hash(seed, i, C.HASH_SALT) - 0.5) * C.JITTER;
    pts.push([cx + Math.cos(a) * rx * j, cy + Math.sin(a) * ry * j]); }
  return pts.map(([x, y], i) => (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ");
};

/* the draw fraction handed to drawOn: the species' elapsed time over DRAW_S (drawOn clamps and eases it). */
export const calloutDrawF = (k, dur, C = CALLOUT) => k * dur / C.DRAW_S;

/* THE LABEL at k: where it is written, how big it is, and whether the hand has got there yet. `ls` is the
   row's opt-in label_scale (a positive number, else 1). */
export const calloutLabel = (b, pd, k, dur, ls, ease, C = CALLOUT) => {
  const lx = b.x + b.w + C.LABEL_DX + pd, ly = b.y + C.LABEL_DY - pd * C.PAD_DY_K;
  const s = Number.isFinite(+ls) && +ls > 0 ? +ls : 1;
  const pop = ease((k * dur - C.DRAW_S * C.LABEL_AT) / C.LABEL_POP_S);
  return { shown: k * dur > C.DRAW_S * C.LABEL_AT, x: lx, y: ly, pop, scale: (C.LABEL_FROM + C.LABEL_SPAN * pop) * s };
};

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the
   clock, the layer already chosen for the kind's target, and the shared helpers by name - `squigglePath` and
   `SQUIG_DRAW` among them, because the underline form is the SQUIGGLE's stroke and clock, not the ring's. */
export function paintCallout(ctx) {
  const { sp, k, dur, svg, el, resolveTarget, drawOn, ease, hash, seed, squigglePath, SQUIG_DRAW } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  if (sp.form === "underline") {   /* P50 T3 / E56's ONE exception: a ring circles a number or a point on a chart,
       but an underline under a QUOTED PHRASE is the squiggle law (s9.27) - the same hand, the same .sq stroke,
       drawn from `at` over SQUIG_DRAW on the underline's own clock, riding the card's live geometry. */
    drawOn(el("path", "sq", svg, { d: squigglePath(b, seed) }), underlineFrac(k * dur / SQUIG_DRAW));
    return;
  }
  const pd = calloutPad(sp.pad);
  drawOn(el("path", "co", svg, { d: calloutPath(b, seed, pd, hash) }), calloutDrawF(k, dur));
  if (!sp.label) return;
  const L = calloutLabel(b, pd, k, dur, sp.label_scale, ease);
  if (!L.shown) return;
  const tx = el("text", "lab", svg, { x: L.x.toFixed(1), y: L.y.toFixed(1) }); tx.textContent = sp.label;
  tx.setAttribute("transform", "translate(" + L.x.toFixed(1) + " " + L.y.toFixed(1) + ") scale(" + L.scale.toFixed(3) + ") translate(" + (-L.x).toFixed(1) + " " + (-L.y).toFixed(1) + ")");
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.callout = paintCallout;
