/* kinetics/chartxf.mjs - CHART TRANSITIONS (P48 T2, 2026-09-10): the interpolators a chart changes STATE by.
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN chartxf and
   KINETICS:END. Self-contained on purpose: nothing here reads a template symbol; the clock (minJerk, ease.mjs) is
   applied by the caller.
   The law (P48): a transition is a pure interpolation between two states that were both BUILT at load. A rescale
   moves every shared mark from its position under scale A to its position under scale B on one clock; a mark whose
   value leaves the target domain fades as it goes; a mark the target adds fades in where it will stand. Nothing is
   rebuilt per frame - the caller writes attributes from the numbers these functions return, so a seek is the play.
   Bravos (46 s46.7): the picture changes six times a minute, the composition two and a half - a rescale is one of
   the builds inside a held frame that make that possible. */

/* xfLerp - the one blend. u is already on the clock (0..1); outside it clamps, so a transition that has not started
   returns a and one that has ended returns b, exactly (the goldens' contract at both ends). */
export const xfLerp = (a, b, u) => { u = Math.min(1, Math.max(0, u)); return a + (b - a) * u; };

/* xfPoint - a datum's screen position between two scales. mapA / mapB take the DATUM (x, v) and return [px, py]; the
   datum never changes, only where the scale puts it - so a point outside B's window still has a position under B
   (past the plot's edge), which is where it travels to while it fades. */
export const xfPoint = (x, v, mapA, mapB, u) => {
  const a = mapA(x, v), b = mapB(x, v);
  return [xfLerp(a[0], b[0], u), xfLerp(a[1], b[1], u)];
};

/* xfPath - a series' whole path between two scales, as the point list and the SVG `d` the caller writes. */
export const xfPath = (pts, mapA, mapB, u) => {
  const out = pts.map(([x, v]) => xfPoint(x, v, mapA, mapB, u));
  return { pts: out, d: out.map(([px, py], k) => (k ? "L" : "M") + px.toFixed(1) + " " + py.toFixed(1)).join(" ") };
};

/* xfFade - the opacity of a mark keyed by VALUE as the domain moves. A mark whose value is inside the target domain
   holds; one leaving fades over the first LEAVE share of the clock; one arriving (present only in B) fades in over the
   last ARRIVE share. Both edges clamp so the ends are exact: at u=0 an arriving mark is invisible, at u=1 a leaving
   one is. */
export const XF = Object.freeze({
  LEAVE: 0.5,    /* a leaving tick is gone by half the clock - it should not travel the whole way as a ghost [DERIVED: E28, the axis must read at every t] */
  ARRIVE: 0.5,   /* an arriving tick appears over the second half, at its settled place */
});
export const xfFade = (inside, arriving, u) => {
  u = Math.min(1, Math.max(0, u));
  if (arriving) return inside ? Math.min(1, Math.max(0, (u - (1 - XF.ARRIVE)) / XF.ARRIVE)) : 0;
  return inside ? 1 : Math.max(0, 1 - u / XF.LEAVE);
};

/* xfInside - is a value within a domain [lo, hi] (either order), with a hair of tolerance for the tick that sits on
   the edge (a nice-step tick at exactly the domain's end is part of the axis, not outside it). */
export const xfInside = (v, lo, hi) => {
  const a = Math.min(lo, hi), b = Math.max(lo, hi), eps = (b - a) * 1e-6;
  return v >= a - eps && v <= b + eps;
};

/* xfRect - a bar between two states: every edge lerps, so a bar that grows keeps its baseline and a bar that moves keeps
   its width law. geom is {x, y, w, h}. */
export const xfRect = (ga, gb, u) => ({ x: xfLerp(ga.x, gb.x, u), y: xfLerp(ga.y, gb.y, u), w: xfLerp(ga.w, gb.w, u), h: xfLerp(ga.h, gb.h, u) });
