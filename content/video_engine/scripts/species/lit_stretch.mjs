/* SPACE: page */
/* species/lit_stretch.mjs - THE LIT STRETCH (P69 T36; the Bravos harvest v2's rank 1, A11 "a stretch relights" with
   A13's comet head; E99 s99). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between
   KINETICS:BEGIN lit_stretch and KINETICS:END, AFTER ease and span (it reads minJerk and the span's edge law). Its
   region sits with the kinetics laws, beside the span's, for the reason span.mjs gives: a PAGE species' math is
   called by the page's PERFORM layer, and a const has to exist before the function that closes over it is built.

   WHEN (`SPECIES_WHEN["lit_stretch"]`, build_scene_timeline_f.py): the sentence WALKS one stretch of a drawn line -
   "the fall", "the run-up", "crashed by nearly two-thirds" - and a light runs along exactly that stretch on the word.

   THE RULING. E99 s99 (the operator, 2026-09-23): "Light can become motion when it's highlighting and moving along a
   length, blinking ... Bravos does this well." A light that TRAVELS counts as motion; a light that simply SITS on a
   thing stays an annotation with 0 motion events (s91). So the light here has one job and it is the travel: the head
   runs from `from` to `to` along the series by arc length on the min-jerk clock, the stretch behind it stays lit, and
   once it has landed it HOLDS - an annotation now, the travel was the event. E99 s71 still stands beside it: a light
   is never the MOVE when a named thing should ARRIVE. This light arrives on nothing new; it walks data the page has
   already drawn, which is why it is a page species and why it never runs ahead of the ink (litClipX).

   THE LAW, a pure function of t:
     the stretch - the named series' own LIVE points from `from` to `to` (a datum index each, or an x-fraction each -
                   the SPAN's edge law, spanEdgeX, imported rather than restated), in TRAVEL order: `from` > `to` runs
                   the other way. Re-read every frame (R26-28): a rescale moves the light with the data, and an edge the
                   window has dropped lights nothing rather than the wrong stretch.
     the travel  - the head sits at minJerk((t - at) / (dur * TRAVEL)) of the stretch's LENGTH; the lit path is the
                   stretch from `from` to the head. After TRAVEL of the word the whole stretch stands lit and holds.
     the ink     - the lit path is clipped to the x the series' own strokes have DRAWN this frame (litDrawnX): a light on
                   a stretch the pen has not reached, or has un-drawn, lights nothing there.
     the head    - `comet: true` puts a bright point with a halo at the head while it travels (A13); it fades over
                   HEAD_OUT_S once the light has landed.
     the leave   - an undraw of the page's line (or of this series) or a `chart_to` that REPLACES the page (recast,
                   morph, remake) takes the light on the verb's own clock, and it does not come back - the bracket's
                   rule (paintBracket's `ud`), resolved once by the builder into `sd.leave`.
   The look is R26-228's electric, not a new one: the lit core is the series' own stroke widened by CORE_K, with a
   drop-shadow halo (lpBloom's form) at GLOW_K; its default colour is the relight's sunflower (PS.RELIGHT_COL), so a
   light on this page reads as the light the page already uses. The dials are ours to tune (42 s42.5), not findings:
   the harvest's open question 3 (the travelling glow's speed per unit of arc, timed at 10 fps) is still unmeasured. */
import { minJerk } from "../kinetics/ease.mjs";
import { spanEdgeX, spanIsIndex, spanActiveState } from "./span.mjs";

export const LIT = Object.freeze({
  TRAVEL: 0.8,       /* the share of the word the head takes to run the stretch: it lands inside the word, never after it */
  CORE_K: 1.6,       /* the lit core's width as a multiple of the series' own stroke - wider, or it hides under the line */
  GLOW_K: 3.2,       /* the halo's radius, the same multiple (lpBloom's drop-shadow, in the chart's own units) */
  GLOW_A: 0.85,      /* ... and its alpha: a light, not a tint */
  HEAD_K: 2.2,       /* the comet head's radius, a multiple of the series' stroke */
  HEAD_OUT_S: 0.35,  /* the head fades over this once the light has landed; the stretch stays lit */
  MIN_LEN: 0.5,      /* a lit length under this is nothing: a round-capped zero-length path paints a dot (E50, "dots that linger") */
});

const lit01 = (v) => Math.min(1, Math.max(0, v));

/* the line's y at an x, read between its own two points (the stretch's fraction edges cut the line there) */
const litYAt = (entries, x) => {
  for (let k = 1; k < entries.length; k++) {
    const [x0, y0] = entries[k - 1].p, [x1, y1] = entries[k].p;
    if ((x - x0) * (x - x1) <= 0) return x1 === x0 ? y1 : y0 + (y1 - y0) * ((x - x0) / (x1 - x0));
  }
  return null;
};

/* THE STRETCH in travel order, or null: the series' own points between the two edges, with a fraction edge cut into
   the line at its x. `entries` is lpPointsNow's shape, [{i, p: [x, y]}] in index order. */
export const litStretchPts = (entries, from, to) => {
  if (!Array.isArray(entries) || entries.length < 2 || from === to) return null;
  let out;
  if (spanIsIndex(from) && spanIsIndex(to)) {
    const lo = Math.min(from, to), hi = Math.max(from, to);
    if (!entries.some((q) => q.i === lo) || !entries.some((q) => q.i === hi)) return null;   /* R26-28: the window dropped an edge */
    out = entries.filter((q) => q.i >= lo && q.i <= hi).map((q) => [q.p[0], q.p[1]]);
  } else {
    const a = spanEdgeX(entries, from), b = spanEdgeX(entries, to);
    if (a === null || b === null) return null;
    const x0 = Math.min(a, b), x1 = Math.max(a, b), y0 = litYAt(entries, x0), y1 = litYAt(entries, x1);
    if (y0 === null || y1 === null) return null;
    out = [[x0, y0], ...entries.filter((q) => q.p[0] > x0 && q.p[0] < x1).map((q) => [q.p[0], q.p[1]]), [x1, y1]];
  }
  if (out.length < 2) return null;
  const reverse = spanIsIndex(from) && spanIsIndex(to) ? from > to : spanEdgeX(entries, from) > spanEdgeX(entries, to);
  return reverse ? out.reverse() : out;
};

export const litLength = (pts) => {
  let L = 0;
  for (let k = 1; k < (pts || []).length; k++) L += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
  return L;
};

/* the stretch's first `s` units of length: its last point is the head */
export const litCut = (pts, s) => {
  if (!pts || !pts.length) return [];
  const out = [[pts[0][0], pts[0][1]]];
  let left = Math.max(0, s);
  for (let k = 1; k < pts.length; k++) {
    const [x0, y0] = pts[k - 1], [x1, y1] = pts[k], seg = Math.hypot(x1 - x0, y1 - y0);
    if (seg <= 0) continue;
    if (left >= seg) { out.push([x1, y1]); left -= seg; continue; }
    if (left > 0) out.push([x0 + (x1 - x0) * (left / seg), y0 + (y1 - y0) * (left / seg)]);
    return out;
  }
  return out;
};

/* THE INK: a line is drawn left to right, so what the pen has laid down is everything at x <= xMax. The lit path keeps
   its part inside that, cut at xMax where it crosses. `xMax` null means nothing measured it - nothing is clipped. */
export const litClipX = (pts, xMax) => {
  if (xMax === null || xMax === undefined || !Number.isFinite(+xMax)) return pts;
  const out = [];
  for (let k = 0; k < pts.length; k++) {
    const q = pts[k];
    if (q[0] <= xMax) { out.push(q); continue; }
    const p = pts[k - 1];
    if (p && p[0] < xMax) out.push([xMax, p[1] + (q[1] - p[1]) * ((xMax - p[0]) / (q[0] - p[0]))]);
    break;
  }
  return out;
};

/* how far THIS series' own strokes are drawn this frame, in the chart's x: the widest of them (a highlighted tail and
   its muted history are two strokes of one series). Read off the stroke's own dash, which the chart painted before the
   perform layer runs - a read of this frame's own ink, so a seek is still the play. null: no stroke of the series. */
export const litDrawnX = (paths, si) => {
  let x = null;
  for (const pp of paths || []) {
    if (!pp || (pp.si | 0) !== (si | 0) || !pp.p || typeof pp.p.getPointAtLength !== "function" || !(pp.len > 0)) continue;
    const hidden = pp.p.style && pp.p.style.opacity === "0";
    const f = hidden ? 0 : lit01(1 - (+pp.p.getAttribute("stroke-dashoffset") || 0) / pp.len);
    const q = pp.p.getPointAtLength(pp.len * f);
    if (q && Number.isFinite(q.x)) x = x === null ? q.x : Math.max(x, q.x);
  }
  return x;
};

/* THE POSE at t: is it up, how far has the head run (0..1 of the stretch's length, eased), is the head showing */
export const litPose = (sp, t) => {
  const at = +sp.at, dur = Math.max(0.001, +sp.dur || 1), T = dur * LIT.TRAVEL, d = t - at;
  const u = d >= T ? 1 : lit01(minJerk(lit01(d / T)));   /* it LANDS whole, and min-jerk's float tail (1.0000000000000002 a hair before T) never overshoots the stretch */
  return { on: d >= 0, u, head: d < 0 ? 0 : lit01(1 - (d - T) / LIT.HEAD_OUT_S) };
};

/* THE LEAVE: `lv` is the builder's {at, dur} of the verb that takes the line, or null (the light stands) */
export const litLeave = (lv, t) => (lv && Number.isFinite(+lv.at) ? minJerk(lit01((t - +lv.at) / Math.max(0.001, +lv.dur || 1))) : 0);

export const litPathD = (pts) => (pts || []).map(([x, y], k) => (k ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ");

/* THE PAINTER (P69 T36). `sd` is the perform layer's built light (`g`, the lit `core` path, the comet `head` or null,
   the series `si`, the declaration `sp` and its resolved `leave`), `st` the page state and `ctx` the PAGE species
   context - `pointsNow` is lpPointsNow, handed in by name, so `node --test` calls this with recorders and no DOM. */
export const paintLitStretch = (sd, t, st, ctx) => {
  const pose = litPose(sd.sp, t), lv = litLeave(sd.leave, t);
  const hide = () => { sd.g.setAttribute("opacity", 0); if (sd.head) sd.head.setAttribute("opacity", 0); };
  if (!pose.on || lv >= 1) { hide(); return; }
  const full = litStretchPts(ctx.pointsNow(st, sd.si), sd.sp.from, sd.sp.to);
  if (!full) { hide(); return; }   /* R26-28: an edge the window dropped lights nothing */
  const S = spanActiveState(st);
  const lit = litClipX(litCut(full, pose.u * litLength(full)), litDrawnX((S && S.paths) || [], sd.si));
  if (lit.length < 2 || litLength(lit) < LIT.MIN_LEN) { hide(); return; }
  sd.core.setAttribute("d", litPathD(lit));
  sd.g.setAttribute("opacity", (1 - lv).toFixed(3));
  if (sd.head) {
    const [hx, hy] = lit[lit.length - 1];
    sd.head.setAttribute("cx", hx.toFixed(1)); sd.head.setAttribute("cy", hy.toFixed(1));
    sd.head.setAttribute("opacity", pose.head.toFixed(3));
  }
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.lit_stretch = paintLitStretch;
