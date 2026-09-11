/* species/span.mjs - THE SPAN (P50 T4; BACKLOG R26-25, the intake's Archetype 5; Bravos shots 107-110's
   "Decades" bracket). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between
   KINETICS:BEGIN span and KINETICS:END. It imports nothing, and its region sits with the kinetics laws
   rather than in the species block at the foot of the file - on purpose: a PAGE species' math is called by
   the page's PERFORM layer, which is written hundreds of lines above the species block, and a const has to
   exist before the function that closes over it is built.

   WHEN: the sentence SPANS a period on a chart - a regime, an epoch, "the decade" - shaded behind the line
   with its name. A BRACKET measures two data; a SPAN names a stretch of time. That is the whole difference,
   and it is why this is a second species and not a bracket option: a bracket's label is a NUMBER it measured,
   a span's label is a NAME it gives.

   THE LAW, a pure function of t:
     shade  - the band between the two declared edges fades in over IN_S to ALPHA, behind every line (it is
              ground, not ink on top - the same rule the spread follows).
     label  - written above the band BY THE HAND, glyph after glyph, over WRITE of the word, starting when
              the shade is in. Above the band where there is room for it, inside its top edge where there
              is not (a chart that fills its box has nothing over it).
   THE EDGES. `from` and `to` are each either a DATUM INDEX (an integer: the page's own index, the one a
   bracket and a figure use) or an X-FRACTION (a number in 0..1 along the drawn series' own x extent, for a
   period that falls between two data). Both are resolved on the ACTIVE chart state every frame, from the
   same live points a bracket reads (R26-28): a rescale moves the band with the data, and a window that has
   dropped one of the two edges hides it rather than drawing it in the wrong place.

   THE PAINTER IS NOT HERE, and that is a finding, not an omission (P50 T4, 2026-09-11): a PAGE species is
   built and painted by the page's own perform layer - inside the chart's viewBox, on the page state `st`,
   under the active state's park transform - while SPECIES_PAINTERS hands a painter the stage-px overlay and
   the scene's clock. Registering a page species in that registry would paint it in the wrong space and leave
   the perform layer none the wiser. So the MATH is here, pure and tested, and the perform layer calls it in
   a dozen lines. Closing that gap - one registry both layers can route through - is P51 T1's business.
   The dials below are ours to tune (42 s42.5), not findings. */

export const SPAN = Object.freeze({
  IN_S: 0.45,       /* the shade's fade-in: a period ARRIVES, it does not cut in - slower than a bracket's tick, because nothing is being measured */
  ALPHA: 0.16,      /* ... and what it settles at: enough to read as a region behind the line, never enough to fight it (the spread bleeds to 0.30 because the gap IS its argument; a span is only the room the argument happens in) */
  WRITE: 0.5,       /* the share of the word the label's hand takes, after the shade is in */
  PAD_T: 44,        /* the band's reach above the highest point of the drawn data, in the chart's viewBox units ... */
  PAD_B: 44,        /* ... and below the lowest: it is a band behind the chart, not a box around the line */
  LABEL_DY: 16,     /* the label's baseline above the band's top edge, where the band has room above it ... */
  LABEL_IN: 2.1,    /* ... and, where it does not, inside the top edge by this many of the label's own sizes: two lines down, clear of the plot's own top furniture (the unit caption sits on the first line inside the plot - read in the frame, 2026-09-11) */
  LABEL_ROOM: 1.3,  /* "room above" means this many label sizes clear of the chart's top - otherwise the name is written inside the band */
  MIN_W: 6,         /* a band narrower than this is not a period - it is two adjacent data, which is a bracket's job */
});

const span01 = (v) => Math.min(1, Math.max(0, v));

/* is this edge a DATUM INDEX (an integer) or an X-FRACTION? */
export const spanIsIndex = (v) => Number.isInteger(v);

/* ONE EDGE -> x in the chart's viewBox. `entries` is the series' live points in lpPointsNow's shape,
   [{i, p: [x, y]}]: an index resolves to the point that CARRIES it (a window that dropped it -> null), a
   fraction to that position along the drawn series' own x extent. */
export const spanEdgeX = (entries, v) => {
  if (!Array.isArray(entries) || entries.length < 2) return null;
  if (spanIsIndex(v)) { const e = entries.find((q) => q.i === v); return e ? e.p[0] : null; }
  const f = +v;
  if (!Number.isFinite(f)) return null;
  const a = entries[0].p[0], b = entries[entries.length - 1].p[0];
  return a + span01(f) * (b - a);
};

/* the band's vertical reach: every drawn series' points, padded - so the shade stands behind the whole
   chart and moves with it, and never has to be told where the plot box is */
export const spanExtent = (lists) => {
  let y0 = Infinity, y1 = -Infinity;
  for (const l of lists || []) for (const q of (l || [])) { y0 = Math.min(y0, q.p[1]); y1 = Math.max(y1, q.p[1]); }
  return Number.isFinite(y0) && Number.isFinite(y1) ? { y0: y0 - SPAN.PAD_T, y1: y1 + SPAN.PAD_B } : null;
};

/* THE BAND this frame, or null when either edge has left the window (the bracket's rule: nothing to name,
   nothing drawn). `entries` is the named series' live points, `lists` every series', `H` the chart's viewBox
   height when the caller knows it - the band is clipped to the page rather than drawn off it. */
export const spanBand = (entries, lists, from, to, H) => {
  const a = spanEdgeX(entries, from), b = spanEdgeX(entries, to), ext = spanExtent(lists);
  if (a === null || b === null || !ext) return null;
  const x0 = Math.min(a, b), x1 = Math.max(a, b);
  if (!(x1 - x0 >= SPAN.MIN_W)) return null;
  const top = Number.isFinite(H) ? Math.max(0, ext.y0) : ext.y0;
  const bot = Number.isFinite(H) ? Math.min(H, ext.y1) : ext.y1;
  if (!(bot > top)) return null;
  return { x: x0, w: x1 - x0, y: top, h: bot - top, cx: (x0 + x1) / 2 };
};

/* where the name is written: above the band when the chart leaves room over it, inside its top edge when
   the chart fills its box (the bracket's own rule for a label with nowhere to stand) */
export const spanLabelY = (band, fs) => (band.y >= fs * SPAN.LABEL_ROOM ? band.y - SPAN.LABEL_DY : band.y + fs * SPAN.LABEL_IN);

/* THE POSE at t: is it up, how deep is the shade, how far has the hand written. */
export const spanPose = (sp, t) => {
  const at = +sp.at, dur = Math.max(0.001, +sp.dur || 1), d = t - at;
  const shade = span01(d / SPAN.IN_S);
  return { on: d >= 0, shade, alpha: SPAN.ALPHA * shade, write: span01((d - SPAN.IN_S) / (dur * SPAN.WRITE)) };
};

/* one glyph's opacity as the hand writes the label: each glyph over its share of the write, with the 1.6
   overlap the bracket and the figure use, so the line reads as a hand and not as a ticker. The share is
   1 / (n + 0.6), not 1 / n, so the LAST glyph is fully in exactly when the write ends - at 1 / n the tail
   of the name would still be at 0.625 when the word was over (the bracket buys the same slack by writing
   its label over only part of its own window). */
export const spanGlyph = (write, j, n) => {
  const per = 1 / (Math.max(1, n | 0) + 1.6 - 1);
  return span01((write - j * per) / (per * 1.6));
};
