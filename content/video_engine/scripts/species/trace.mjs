/* SPACE: stage */
/* species/trace.mjs - THE ROUTE ON A STILL (P57 T18 / R26-95; the STILL LIFE species of 2026-09-05 - "the arrow
   on the phone redraws" - and the opt-in bowed HOP of 2026-09-08, the crossings map the approved Japan short
   ships at t 9.22).
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN trace
   and KINETICS:END, AFTER callout - it imports nothing, so its place in the order is only a place.

   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the engine's body.
   The last statement registers the painter in SPECIES_PAINTERS; node, where no such registry exists, still
   imports the file for the pure math below. Promoted from inline engine code (`paintSpecies sp.kind ===
   "trace"`) with every golden byte-identical: each literal below is the value the inline code carried, to the
   digit, and no expression was re-associated.

   WHEN (`SPECIES_WHEN["trace"]`, build_scene_timeline_f.py:323, verbatim): "the sentence NAMES places and flows
   on a still - a route draws with hops between named points, stamps stack at them".

   THE LAW - the still-life law (the operator, 2026-09-05) and E49 (nothing ever goes truly still): a picture we
   cannot re-shoot is given its own small life, and that life is a PURE FUNCTION OF t - the plain trace redraws
   itself on its own period, so a cold seek into the middle of a hold lands exactly where a play does, and the
   jitter's only source is the seeded hash, never Math.random. The `hop` is the ONE crossing form, and what may
   be declared on it is the COMPILER's (`build_scene_timeline_f.py:1344` - from / to as stage fractions 0..1,
   bow / draw_s / width numbers, draw_s > 0); the painter carries no opinion about where it was pointed.

   THE FORM, all of it a pure function of t:
     the trace - a seeded zigzag down the region's own diagonal: N + 1 points from (X0, Y0) to (X0 + X_SPAN,
                 Y0 + Y_SPAN) of the box, every interior point jogged by up to half of JAG_K of the box's
                 height off the seeded hash. It draws on by dash over DRAW_S, holds, fades over the last
                 FADE_SPAN of the period, and goes again every PERIOD - a still life, not an event.
     the hop   - ONE quadratic bow from point to point in STAGE fractions, sampled to the SAME N + 1 points, so
                 the arrowhead law below is shared: the control point is the chord's midpoint pushed along the
                 chord's normal by bow x BOW_K x the chord's own length (the sign is the side). Drawn ONCE over
                 hop.draw_s and HELD to the end of dur - a crossing, not a redraw.
     the head  - when the line lands (drawK >= 1), two strokes back from the last point at +/- HEAD_A radians
                 off the last segment's angle, HEAD_K stroke-widths long on a hop and HEAD_W of the box's width
                 on a trace. It carries the line's own opacity, so the two arrive and leave as one mark.
   Nothing is stored: every visual reads from t, k, dur and the seed. The dials below are ours to tune
   (42 s42.5), not findings. */

export const TRACE = Object.freeze({
  PERIOD: 3.2,        /* the plain trace's whole redraw cycle, in seconds [the engine's SP.TRACE_PERIOD, verbatim] */
  DRAW_S: 1.1,        /* ... of which this is the draw [SP.TRACE_DRAW] - and a hop's draw when it declares none */
  N: 7,               /* the segments both forms are sampled to: a hand's line, and one arrowhead law for both */
  MIN_DRAW_S: 0.05,   /* the floor under a declared hop.draw_s, so no division by zero reaches the dash */
  BOW: 0.18,          /* a hop's default arc height, as a fraction of the chord (signed for the side) ... */
  BOW_K: 2,           /* ... doubled into the quadratic's control point, which a curve passes at half its offset */
  JAG_K: 0.35,        /* the zigzag's jog: +/- half of this, times the box's height, off the seeded hash */
  HASH_SALT: 44,      /* the salt that jitter's hash is taken with - the trace's own stream (steam 41-43, ticker 45-47) */
  X0: 0.08,           /* the zigzag's first point, as a fraction of the box ... */
  X_SPAN: 0.84,       /* ... and how far across it runs (inset both ends: a mark on a picture, not an edge) */
  Y0: 0.12,
  Y_SPAN: 0.76,
  WIDTH: 7,           /* a hop's stroke width when it declares none ... */
  WIDTH_K: 0.045,     /* ... and a plain trace's, as a fraction of the box's width ... */
  WIDTH_MIN: 3,       /* ... with this floor, so a small region still reads at phone size */
  FADE_AT: 0.82,      /* the plain trace holds until this far through its period ... */
  FADE_SPAN: 0.18,    /* ... then fades out over the rest of it (the two are the whole period by construction) */
  IN_S: 0.4,          /* the species' own fade in - and out, which a hop does not take (it is held) */
  HEAD_K: 3,          /* a hop's arrowhead, in stroke widths ... */
  HEAD_MIN: 8,        /* ... a plain trace's, floored here ... */
  HEAD_W: 0.12,       /* ... and taken as this fraction of the box's width */
  HEAD_A: 0.5,        /* each barb's angle off the last segment, in radians */
  COLOR: "#B0201F",   /* the mark's colour when the row declares none: the ledger's own red */
});

/* THE HOP the row declared, or none. Both ends are required - a hop with one end is not a crossing, and the
   plain still-life trace is what the species is without it (the compiler checks the rest). */
export const traceHopOf = (sp) => (sp.hop && sp.hop.from && sp.hop.to ? sp.hop : null);

/* WHERE IN ITS PERIOD the plain trace is at t: 0..1 from the species' own `at`, and 0 for a hop, which has no
   period at all - it is drawn once and held. */
export const tracePhase = (t, at, hop, T = TRACE) => (hop ? 0 : (((t - at) / T.PERIOD) % 1 + 1) % 1);

/* THE DRAW FRACTION handed to drawOn: a hop's own elapsed time over its draw, a trace's phase over the draw's
   share of the period. `clamp` is handed in (the engine's clamp01) - the same one the inline code used. */
export const traceDrawK = (t, at, hop, ph, clamp, T = TRACE) =>
  (hop ? clamp((t - at) / Math.max(T.MIN_DRAW_S, +hop.draw_s || T.DRAW_S)) : clamp(ph * T.PERIOD / T.DRAW_S));

/* THE HOP as N + 1 points in stage px: a quadratic bow whose control point is the chord's midpoint pushed along
   the chord's NORMAL by bow x BOW_K x the chord's length. `from` / `to` are stage fractions (the compiler's law). */
export const traceHopPoints = (hop, stageW, stageH, T = TRACE) => {
  const n = T.N, pts = [];
  const x0 = hop.from[0] * stageW, y0 = hop.from[1] * stageH, x1 = hop.to[0] * stageW, y1 = hop.to[1] * stageH;
  const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, dx = x1 - x0, dy = y1 - y0, L0 = Math.hypot(dx, dy) || 1;
  const bow = Number.isFinite(+hop.bow) ? +hop.bow : T.BOW, cx2 = mx - dy / L0 * bow * L0 * T.BOW_K, cy2 = my + dx / L0 * bow * L0 * T.BOW_K;
  for (let i = 0; i <= n; i++) { const u = i / n, v = 1 - u;
    pts.push([v * v * x0 + 2 * v * u * cx2 + u * u * x1, v * v * y0 + 2 * v * u * cy2 + u * u * y1]); }
  return pts;
};

/* THE PLAIN TRACE as N + 1 points in stage px: down the box's diagonal, every INTERIOR point jogged off the
   seeded `hash` (the engine's lpHash in the player, a stub under node) - never Math.random. */
export const tracePlainPoints = (b, seed, hash, T = TRACE) => {
  const n = T.N, pts = [];
  for (let i = 0; i <= n; i++) {
    const s2 = i / n, jag = i && i < n ? (hash(seed, i, T.HASH_SALT) - 0.5) * b.h * T.JAG_K : 0;
    pts.push([b.x + b.w * (T.X0 + T.X_SPAN * s2), b.y + b.h * (T.Y0 + T.Y_SPAN * s2) + jag]);
  }
  return pts;
};

/* the sampled points as a path, in stage px - one line, so both forms draw the same way */
export const tracePathD = (pts) => pts.map(([x, y], i) => (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ");

/* THE STROKE WIDTH: a hop's declared one (or the dial), a trace's from the box it crosses, floored. */
export const traceWidth = (hop, b, T = TRACE) =>
  (hop ? (Number.isFinite(+hop.width) ? +hop.width : T.WIDTH) : Math.max(T.WIDTH_MIN, b.w * T.WIDTH_K));

/* THE OPACITY at k: the plain trace's own fade at the end of its period, times the species' fade in and out -
   which a hop takes on the way in only, because it is HELD to the end of dur. */
export const traceOpacity = (ph, k, dur, hop, clamp, T = TRACE) => {
  const fade = hop ? 1 : (ph > T.FADE_AT ? 1 - (ph - T.FADE_AT) / T.FADE_SPAN : 1);
  return fade * clamp(Math.min(k * dur / T.IN_S, hop ? 1 : (1 - k) * dur / T.IN_S));
};

/* THE ARROWHEAD, as a path: two barbs back from the last point along the last segment's own angle. It is drawn
   only when the line has landed, which is the whole point - the head lands when the line does. */
export const traceHead = (pts, sw, hop, b, T = TRACE) => {
  const n = T.N;
  const [ax, ay] = pts[n], [bx2, by2] = pts[n - 1], ang = Math.atan2(ay - by2, ax - bx2), L2 = hop ? sw * T.HEAD_K : Math.max(T.HEAD_MIN, b.w * T.HEAD_W);
  return "M" + (ax - L2 * Math.cos(ang - T.HEAD_A)).toFixed(1) + " " + (ay - L2 * Math.sin(ang - T.HEAD_A)).toFixed(1) + " L" + ax.toFixed(1) + " " + ay.toFixed(1) + " L" + (ax - L2 * Math.cos(ang + T.HEAD_A)).toFixed(1) + " " + (ay - L2 * Math.sin(ang + T.HEAD_A)).toFixed(1);
};

/* the mark's stroke, shared by the line and its head so the two read as one hand */
export const traceStroke = (sp, sw, T = TRACE) =>
  ({ stroke: sp.color || T.COLOR, "stroke-width": sw.toFixed(1), fill: "none", "stroke-linejoin": "round", "stroke-linecap": "round" });

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the clock,
   the layer already chosen for the kind's target, and the shared helpers by name. */
export function paintTrace(ctx) {
  const { sp, k, dur, t, svg, el, resolveTarget, drawOn, clamp, hash, seed, STAGE_W, STAGE_H } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  const hop = traceHopOf(sp);
  const ph = tracePhase(t, sp.at, hop), drawK = traceDrawK(t, sp.at, hop, ph, clamp);
  const pts = hop ? traceHopPoints(hop, STAGE_W, STAGE_H) : tracePlainPoints(b, seed, hash);
  const sw = traceWidth(hop, b), stroke = traceStroke(sp, sw);
  const p = el("path", "", svg, Object.assign({ d: tracePathD(pts) }, stroke));
  p.setAttribute("opacity", traceOpacity(ph, k, dur, hop, clamp).toFixed(3));
  drawOn(p, drawK);
  if (drawK >= 1) el("path", "", svg, Object.assign({ d: traceHead(pts, sw, hop, b) }, stroke, { opacity: p.getAttribute("opacity") }));
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.trace = paintTrace;
