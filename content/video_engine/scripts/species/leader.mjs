/* SPACE: page */
/* species/leader.mjs - THE LEADER (P72 T53 (h), R26-414 (a); the Bravos harvest v2's R35 "Flow -> the total -> a
   pointer back", STK 0:02-0:10: "$12,000,000,000" arcs to the ringed peak, then the peak arcs back to the small bar it
   dwarfs with "10x" on the arc). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between
   KINETICS:BEGIN leader and KINETICS:END, AFTER ease, spring, clothoid, level_join and axis_tag (it reads their laws).
   Its region sits with the page species', after axis_tag's and before buildPerform / paintPerform, for the reason
   span.mjs gives.

   WHEN (`SPECIES_WHEN["leader"]`, build_scene_timeline_f.py): the sentence POINTS one number back at another - a
   headline total at the bar it dwarfs, a written figure at the datum it came from - and the pointer IS the claim. The
   multiple rides the arc. Don't: point at a thing the page does not draw (the truth rule refuses it), or put a word
   the author typed where the page's arithmetic belongs.

   WHAT IT IS BUILT ON (nothing new is drawn by hand here):
     the arc     - the vector map's ARC law (species/vecmap.mjs arcPath): a CLOTHOID (kinetics/clothoid.mjs) between the
                   two ends, its tangents turned UNEQUALLY off the chord - `bow` at the tail, `bow * ENTER_K` at the tip -
                   so the pen ramps out of the source and settles into the target. vecmap's region sits after
                   paintPerform, so its dials are restated here BY VALUE (BOW, ENTER_K, SAMPLES, HEAD_PX, HEAD_A) and the
                   node test pins them equal.
     the head    - the flow / arc arrowhead (flowHead / arcHead: two strokes along the arriving tangent), in stage px
                   carried into chart units; or a DOT.
     the ends    - the SOURCE's own box (a written figure: species/figure.mjs figBox, handed in by the builder), a datum
                   or a point; the TARGET a datum (a line's point, a bar's top) or a bar's printed VALUE (P72 T18's
                   `part: "value"`, R26-288). The tail leaves the source's edge facing where the arc heads (the flow's
                   edge law, flowAnchors, for a rectangle), the tip stops GAP_PX short of the target's outline.
     the ring    - the ring species' OWN dashes (ring.mjs ringEllipse / ringDashes), handed in by the builder exactly as
                   level_join's end rings are, drawn dash by dash on level_join's per-dash law; a dash on the page's words
                   stays undrawn (levelDashYields). E56: it circles a number or a point on a chart, which a datum is.
     the label   - ON the arc, at half its length: the page's accent capsule (axis_tag's pill box and pop, AXTAG), the
                   multiple the compiler COMPUTED off the two data (never typed; a typed figure is checked against the
                   page's arithmetic, level_join's `_lj_truth`).
     the leave   - the page's own (the compiler's `leave_at`, a page-bound species, R26-219) and an undraw of the line
                   or a verb that replaces the page, at or after the word, on its own clock (levelLeave).
   THE SIDE (which way the arc bows, and how far) is decided ONCE, on the build's geometry: the author's `bend` when
   there is one (E99 s106: the engine advises, the author decides), else the first of up / down x BOWS whose arc and
   pill stay clear of the page's own words and the chart's box - least cost when none is. So a rescale moves the arc
   with its ends and never flips it. Re-read every frame (R26-28): both ends come off the ACTIVE state, so an end the
   window has dropped hides the leader rather than point at the wrong thing. The dials are ours to tune (42 s42.5). */
import { minJerk } from "../kinetics/ease.mjs";
import { springPop } from "../kinetics/spring.mjs";
import { clothoid, clothoidPath } from "../kinetics/clothoid.mjs";
import { levelDashF, levelDashYields, levelLeave } from "./level_join.mjs";
import { AXTAG } from "./axis_tag.mjs";

export const LEADER = Object.freeze({
  SHAFT: [0.0, 0.6],     /* the share of the word the arc draws over, by length, on min-jerk ... */
  HEAD: [0.55, 0.7],     /* ... the head lands as the shaft arrives (the arc's HEAD_F, 0.74 of its own clock) ... */
  RING: [0.45, 0.85],    /* ... the target's ring draws dash by dash round it as the tip approaches ... */
  LABEL: [0.62, 1.0],    /* ... and the multiple's pill POPS on the arc once the arc is most of the way there */
  BOW: 0.5,              /* vecmap ARC.BOW: the tail's turn off the chord, radians - a flight path lifts, it does not hoop */
  ENTER_K: 0.45,         /* vecmap ARC.ENTER_K: the tip's turn as a share of it - unequal, so the fitter's ramp is used */
  SAMPLES: 48,           /* vecmap ARC.SAMPLES: the clothoid's polyline */
  HEAD_PX: 26,           /* vecmap ARC.HEAD: the arrowhead's stroke in stage px ... */
  HEAD_A: 0.42,          /* ... and its half-angle (the flow's arrow: two arrows in one episode are one hand) */
  DOT_PX: 7,             /* the DOT head's radius, stage px (Bravos STK 0:02's small disc at the ring's edge) */
  GAP_PX: 12,            /* the air the tail leaves off its source and the tip stops short of its target, stage px */
  RING_K: 0.8,           /* a ring round a POINT target: the ring species' own minimum ellipse at this scale (level_join's
                            END ring is 0.55; the leader's ring is the answer the arc points at - Bravos's is a callout's) */
  BEND_MAX: 1.1,         /* `bend: +-1` turns the tail this far off the chord (the widest of BOWS) */
  BOWS: Object.freeze([0.5, 0.8, 1.1]),   /* the automatic candidates, each side: the arc's own bow first, then wider */
  WIDE: Object.freeze([1.4, 1.7]),        /* P72 T53 (k) / R26-418 (a): the wide LIFTS, tried only when no candidate above is
                                             clear - over a tall word in the way (9:16: the $121B between the total and the
                                             $28B), into the air above the chart (Bravos STK 0:08's high arc), never a sag */
  WORD_COST: 1000,       /* one arc sample (or the pill) on one of the page's words ... */
  EDGE_COST: 10000,      /* ... off the chart's box ... */
  INK_COST: 1,           /* ... on a mark's ink (a bar): allowed, but a clear arc over air is preferred */
  PILL_PAD_PX: 6,        /* the air the pill keeps off a word, stage px */
  FRAME_COST: 0.25,      /* P72 T53 (k) / R26-418 (b): one arc sample ON the long form's plot-frame border - a quarter of a
                            sample on a bar's ink: a clean crossing (one or two samples) is cheaper than a sag through the
                            bars, an arc RIDING the border (many samples) is not; the chooser then takes the least of them */
  FRAME_PILL_COST: 1000, /* ... and the multiple's pill straddling that border costs as a word does */
  FRAME_PAD_PX: 6,       /* the border's reach either side of its line, stage px */
  SKY_PAD_PX: 12,        /* R26-418 (a): the air an arc lifted into the room above the chart keeps under the page's words */
});

const ld01 = (v) => Math.min(1, Math.max(0, v));
const ldWin = (u, w) => ld01((u - w[0]) / Math.max(1e-6, w[1] - w[0]));

/* THE CLOCK at t: each phase's share (0..1); `on` is false before the word. */
export const leaderPose = (sp, t) => {
  const dur = Math.max(0.001, +sp.dur || 1), u = (t - +sp.at) / dur;
  return { on: u >= 0, shaft: minJerk(ldWin(u, LEADER.SHAFT)), head: ldWin(u, LEADER.HEAD), ring: ldWin(u, LEADER.RING),
           label: ldWin(u, LEADER.LABEL) };
};

/* the pill's scale at t: axis_tag's pop (AXTAG.POP_S, POP_MP) from the label's window */
export const leaderPillScale = (sp, t) => {
  const dur = Math.max(0.001, +sp.dur || 1), d = t - (+sp.at + LEADER.LABEL[0] * dur);
  if (!(d >= 0)) return 0;
  return springPop(ld01(d / AXTAG.POP_S), AXTAG.POP_MP);
};

/* A SHAPE is where an end stands, in chart units: a box [x0, y0, x1, y1] (a written figure, a printed value), an ellipse
   {cx, cy, rx, ry} (a ring round the target) or a point [x, y]. Its centre: */
export const leaderCentre = (s) => (Array.isArray(s) && s.length === 4 ? [(s[0] + s[2]) / 2, (s[1] + s[3]) / 2]
  : s && Number.isFinite(s.rx) ? [s.cx, s.cy] : s);

/* the point on a shape's OUTLINE in direction `th` from its centre, pushed `gap` further out - the flow's edge law
   (flowAnchors: the ray leaves by whichever side it meets first) for a rectangle, the polar radius for an ellipse,
   the point itself for a point */
export const leaderOut = (s, th, gap) => {
  const cs = Math.cos(th), sn = Math.sin(th), c = leaderCentre(s);
  let r = 0;
  if (Array.isArray(s) && s.length === 4) {
    const hw = (s[2] - s[0]) / 2, hh = (s[3] - s[1]) / 2;
    r = Math.min(Math.abs(cs) > 1e-9 ? hw / Math.abs(cs) : Infinity, Math.abs(sn) > 1e-9 ? hh / Math.abs(sn) : Infinity);
  } else if (s && Number.isFinite(s.rx)) {
    r = 1 / Math.sqrt((cs / s.rx) * (cs / s.rx) + (sn / s.ry) * (sn / s.ry));
  }
  return [c[0] + (r + gap) * cs, c[1] + (r + gap) * sn];
};

/* the turn that LIFTS the arc toward the page's top (svg y grows down): vecmap's arcBowSign with the north's w = -1 */
export const leaderUp = (a, b) => (b[0] - a[0] >= 0 ? -1 : 1);

/* THE ARC from shape A to shape B: the tail on A's outline where the arc leaves, the tip on B's where it arrives (each
   `gap` clear), the clothoid between them with vecmap's unequal tangents. `sign` is the turn (+-1), `bow` radians. */
export const leaderArc = (A, B, bow, sign, gaps) => {
  const ca = leaderCentre(A), cb = leaderCentre(B), chord = Math.atan2(cb[1] - ca[1], cb[0] - ca[0]);
  const g = gaps || [0, 0], b = +bow || 0, s = sign < 0 ? -1 : 1;
  const p0 = leaderOut(A, chord + s * b, g[0]), p1 = leaderOut(B, chord - s * b * LEADER.ENTER_K + Math.PI, g[1]);
  const c2 = Math.atan2(p1[1] - p0[1], p1[0] - p0[0]);
  return clothoid(p0, c2 + s * b, p1, c2 - s * b * LEADER.ENTER_K, LEADER.SAMPLES);
};

/* a point `f` of the way along the polyline BY LENGTH, with the heading there */
export const leaderAlong = (pts, f) => {
  const n = pts.length;
  if (n < 2) return n ? { x: pts[0].x, y: pts[0].y, th: 0 } : null;
  let L = 0;
  const cum = [0];
  for (let i = 1; i < n; i++) { L += Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y); cum.push(L); }
  const d = ld01(f) * L;
  let i = 1;
  while (i < n - 1 && cum[i] < d) i++;
  const seg = cum[i] - cum[i - 1], u = seg > 0 ? (d - cum[i - 1]) / seg : 0;
  return { x: pts[i - 1].x + (pts[i].x - pts[i - 1].x) * u, y: pts[i - 1].y + (pts[i].y - pts[i - 1].y) * u,
           th: Math.atan2(pts[i].y - pts[i - 1].y, pts[i].x - pts[i - 1].x) };
};

/* the arrowhead's two strokes at the far end along the tangent it arrives on - arcHead / flowHead's law, its arm `len`
   and half-angle `ang` handed in (chart units on a page) */
export const leaderHead = (pts, len, ang) => {
  const n = pts.length;
  if (n < 2) return "";
  const tip = pts[n - 1], prev = pts[n - 2], th = Math.atan2(tip.y - prev.y, tip.x - prev.x);
  const arm = (s) => ({ x: tip.x - len * Math.cos(th + s * ang), y: tip.y - len * Math.sin(th + s * ang) });
  const l = arm(1), r = arm(-1);
  return "M" + l.x.toFixed(2) + " " + l.y.toFixed(2) + " L" + tip.x.toFixed(2) + " " + tip.y.toFixed(2)
       + " L" + r.x.toFixed(2) + " " + r.y.toFixed(2);
};

const ldIn = (p, b, pad) => p.x >= b[0] - pad && p.x <= b[2] + pad && p.y >= b[1] - pad && p.y <= b[3] + pad;
const ldMeet = (a, b) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];

/* the pill's box at the arc's middle ([w, h] its size), [x0, y0, x1, y1] */
export const leaderPillBox = (pts, size) => {
  const m = leaderAlong(pts, 0.5);
  return m && size ? [m.x - size[0] / 2, m.y - size[1] / 2, m.x + size[0] / 2, m.y + size[1] / 2] : null;
};

/* P72 T53 (k) / R26-418 (b): is a point ON the plot frame's border ([x0, y0, x1, y1], reach `r` either side of a line)? */
const ldOnFrame = (p, f, r) => {
  const inX = p.x >= f[0] - r && p.x <= f[2] + r, inY = p.y >= f[1] - r && p.y <= f[3] + r;
  return (inX && (Math.abs(p.y - f[1]) <= r || Math.abs(p.y - f[3]) <= r)) || (inY && (Math.abs(p.x - f[0]) <= r || Math.abs(p.x - f[2]) <= r));
};
/* ... and does a box straddle one of its lines? */
const ldBoxOnFrame = (b, f) => {
  const inX = b[2] > f[0] && b[0] < f[2], inY = b[3] > f[1] && b[1] < f[3];
  return (inX && ((b[1] < f[1] && b[3] > f[1]) || (b[1] < f[3] && b[3] > f[3]))) || (inY && ((b[0] < f[0] && b[2] > f[0]) || (b[0] < f[2] && b[2] > f[2])));
};

/* THE COST of one arc: its samples on the page's WORDS dominate, then off the chart's box, then on a mark's ink, then
   on the plot frame's border; the pill on a word, off the box or across the frame's border costs as a word does.
   `g`: {words, ink ([x0, y0, x1, y1] each), W, H, pill: [w, h] | null, pad (the pill's air, chart units), top? (R26-418
   (a): the free room above the chart's box the builder measured, a y <= 0 - the box's top edge moves up to it; absent,
   0), frame? ([x0, y0, x1, y1] the long form's plot frame, R26-418 (b); absent, none), framePad? (its reach)}. */
export const leaderCost = (pts, g) => {
  let c = 0;
  const words = g.words || [], ink = g.ink || [], W = +g.W, H = +g.H, box = Number.isFinite(W) && Number.isFinite(H);
  const top = Number.isFinite(+g.top) ? Math.min(0, +g.top) : 0, fr = Array.isArray(g.frame) && g.frame.length === 4 ? g.frame : null;
  const fp = +g.framePad || 0;
  for (const p of pts) {
    for (const w of words) if (ldIn(p, w, 0)) c += LEADER.WORD_COST;
    for (const b of ink) if (ldIn(p, b, 0)) c += LEADER.INK_COST;
    if (box && (p.x < 0 || p.x > W || p.y < top || p.y > H)) c += LEADER.EDGE_COST;
    if (fr && ldOnFrame(p, fr, fp)) c += LEADER.FRAME_COST;
  }
  const pb = leaderPillBox(pts, g.pill), pad = +g.pad || 0;
  if (pb) {
    const grown = [pb[0] - pad, pb[1] - pad, pb[2] + pad, pb[3] + pad];
    for (const w of words) if (ldMeet(grown, w)) c += LEADER.WORD_COST;
    if (box && (pb[0] < 0 || pb[2] > W || pb[1] < top || pb[3] > H)) c += LEADER.EDGE_COST;
    if (fr && ldBoxOnFrame(grown, fr)) c += LEADER.FRAME_PILL_COST;
  }
  return c;
};

/* THE SIDE, decided once: the author's `bend` (+ lifts toward the page's top, - sags, 0 straight; |bend| x BEND_MAX
   radians) when there is one, else the first of up x BOWS then down x BOWS - then (R26-418 (a)) up x WIDE - whose cost
   is 0, else the cheapest. The wide lifts come LAST, so every page that had a clear candidate keeps it. */
export const leaderChoose = (A, B, g, bend) => {
  const up = leaderUp(leaderCentre(A), leaderCentre(B)), gaps = g.gaps || [0, 0];
  if (bend !== undefined && bend !== null && Number.isFinite(+bend)) {
    const b = Math.max(-1, Math.min(1, +bend));
    const pick = { sign: b >= 0 ? up : -up, bow: Math.abs(b) * LEADER.BEND_MAX, authored: true };
    return Object.assign(pick, { cost: leaderCost(leaderArc(A, B, pick.bow, pick.sign, gaps), g) });
  }
  let best = null;
  const cands = [...[up, -up].flatMap((s) => LEADER.BOWS.map((bow) => [s, bow])), ...LEADER.WIDE.map((bow) => [up, bow])];
  for (const [s, bow] of cands) {
    const c = leaderCost(leaderArc(A, B, bow, s, gaps), g);
    if (c === 0) return { sign: s, bow, authored: false, cost: 0 };
    if (!best || c < best.cost) best = { sign: s, bow, authored: false, cost: c };
  }
  return best;
};

/* THE PAINTER (P72 T53 (h)). `sd` is the perform layer's built leader: `g` (the group), `shaft` (a path, pathLength 1),
   `head` ({kind: "arrow" | "dot", el}), `ring` ({g, dashes: [{p, t0, t1, box}], rx, ry} in stage px, or null), `pill`
   ({g, box: {w, h}} or null), `fromShape(st)` / `toShape(st)` (the ends on the ACTIVE state, chart units, null when the
   window dropped one), `pick` ({sign, bow} - the side chosen at build), `k` (stage px per chart unit), `words` (the
   page's own label boxes, [x0, y0, x1, y1]) and `leave` (the verb that takes the line, or null). `ctx` is the PAGE
   species context; this painter needs nothing from it but is handed it like every page painter. */
export const paintLeader = (sd, t, st, ctx) => {
  const sp = sd.sp, pose = leaderPose(sp, t), lv = levelLeave(sd.leave, t);
  const hide = () => { sd.g.setAttribute("opacity", 0); };
  if (!pose.on || lv >= 1) { hide(); return; }
  const A = sd.fromShape(st), T = sd.toShape(st);
  if (!A || !T) { hide(); return; }   /* R26-28: an end the window dropped points at nothing */
  const k = sd.k > 0 ? sd.k : 1, c = leaderCentre(T);
  const B = sd.ring ? { cx: c[0], cy: c[1], rx: sd.ring.rx / k, ry: sd.ring.ry / k } : T;   /* a ringed target: the arc ends at the ring */
  const pts = leaderArc(A, B, sd.pick.bow, sd.pick.sign, [LEADER.GAP_PX / k, LEADER.GAP_PX / k]);
  sd.g.setAttribute("opacity", (1 - lv).toFixed(3));
  sd.shaft.setAttribute("d", clothoidPath(pts));
  sd.shaft.setAttribute("stroke-dashoffset", (1 - pose.shaft).toFixed(4));
  sd.shaft.setAttribute("opacity", pose.shaft > 0 ? 1 : 0);
  const tip = pts[pts.length - 1];
  if (sd.head.kind === "dot") {
    sd.head.el.setAttribute("cx", tip.x.toFixed(2)); sd.head.el.setAttribute("cy", tip.y.toFixed(2));
    sd.head.el.setAttribute("r", (LEADER.DOT_PX / k * pose.head).toFixed(3));
  } else {
    sd.head.el.setAttribute("d", leaderHead(pts, LEADER.HEAD_PX / k, LEADER.HEAD_A));
  }
  sd.head.el.setAttribute("opacity", pose.head.toFixed(3));
  if (sd.ring) {
    sd.ring.g.setAttribute("transform", "translate(" + c[0].toFixed(1) + " " + c[1].toFixed(1) + ") scale(" + (1 / k).toFixed(5) + ")");
    for (const dh of sd.ring.dashes) {
      const q = levelDashF(pose.ring, dh), off = dh.box && levelDashYields(dh.box, c, k, sd.words);   /* a dash on the page's words stays undrawn */
      dh.p.setAttribute("stroke-dashoffset", (1 - q).toFixed(4));
      dh.p.setAttribute("opacity", q > 0 && !off ? 1 : 0);
    }
  }
  if (sd.pill) {
    const s = leaderPillScale(sp, t), m = leaderAlong(pts, 0.5);
    sd.pill.g.setAttribute("opacity", s > 0 ? 1 : 0);
    sd.pill.g.setAttribute("transform", "translate(" + m.x.toFixed(1) + " " + m.y.toFixed(1) + ") scale(" + s.toFixed(4) + ")");
  }
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.leader = paintLeader;
