/* SPACE: page */
/* species/level_join.mjs - THE LEVEL JOIN (P71 T10, was P69 T39; the Bravos harvest v2's A9 "a dashed LEVEL rule drawn
   from one datum to another", n=5, rank 4). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py
   between KINETICS:BEGIN level_join and KINETICS:END, AFTER ease (it reads minJerk). Its region sits with the page
   species', before paintPerform closes over the painter, for the reason span.mjs gives.

   WHEN (`SPECIES_WHEN["level_join"]`, build_scene_timeline_f.py; BRAVOS-USE-WHEN.md A9): the sentence SPANS two numbers
   on one series - "higher than at the depth of 2008", "twenty-eight, the most it has ever been" against the dot-com 23 -
   and the rule JOINS the two data, so the eye reads the gap as a distance. Don't: put the label on the rule (C14).

   THE LAW, a pure function of t:
     the rule   - one dashed HORIZONTAL rule at `from`'s level, from the `from` datum to the far end's x, drawn BY LENGTH
                  from `from` on the min-jerk clock (a rule that travels is motion, E99 s99). The far end is the `to`
                  datum (the same series, or `to: {series, index}` on another series in the same unit) - so the gap
                  between the rule's end and that datum IS the difference, made a distance - or, `to: {y}`, the value
                  AXIS at `from`'s own level (the harvest's DOM 00:50 / BOOM 00:41: from the endpoint to the axis).
                  Its dash is the dashed ring's rhythm (species/ring.mjs RING.DASH / DASH_GAP, stage px), read by the
                  builder: ring.mjs is a STAGE module whose region sits after paintPerform, so it cannot be imported
                  here - the builder hands its law in (`sd.dash`, `sd.gap`, and the ring's own dashes, below).
     the rings  - a dashed ring lands at each end: on `from` as the rule leaves it, on the far end as the rule arrives.
                  They are the ring species' OWN dashes (ringDashes round a point: the MIN_RX x MIN_RY ellipse at
                  RING_K, drawn dash by dash clockwise from the top), built once round the origin by the builder and
                  moved here. A dash that would stand on one of the page's own words (an end tag beside the last datum,
                  a tick label) is not drawn: the ring OPENS toward the word rather than strike through it.
     the label  - the figure the claim turns on, written by the hand glyph by glyph as the far ring closes. It is placed
                  OFF THE RULE BY CONSTRUCTION (C14; the E53 addendum's mislabel): beside the far ring, on the first
                  side of right / the gap's own side (above when the far datum stands over the rule) / the other side /
                  left whose box is clear of the rule, the page's own labels, the series' points and the chart's edge -
                  least overlap when none is. An AUTHORED `side` (and `dy`, lines of its own size) is honoured as
                  written (E99 s106: the engine advises, the author decides); the compiler WARNs, with its numbers, when
                  the authored place lands on the rule. The side is decided ONCE, on the build's geometry, so a rescale
                  moves the label with its ring and never flips it. It is a PEER OF THE END TAG, not a card: on a
                  phone-type page (the long form) it is set at the end tags' own size for the active preset, and where
                  the page draws a PLOT FRAME (the long form's panel) every side's box is nudged inside it, FRAME_AIR
                  clear of the border - left / up first - before the side is chosen (frame read, 2026-09-24: at the
                  phone floor it stood bigger than the end tags and half over the frame's border). A page with no frame
                  (the flat face) is untouched.
     the leave  - the page's own (the compiler's `leave_at`, a page-bound species, R26-219) and an undraw of the page's
                  line (or of this series) at or after the word, on the undraw's own clock (the lit stretch's rule).
   Re-read every frame (R26-28): both anchors come off the ACTIVE state's live points, so a rescale moves the join with
   the data, and an end the window has dropped hides it rather than joining the wrong datum. The dials below are ours
   to tune (42 s42.5), not findings. */
import { minJerk } from "../kinetics/ease.mjs";
import { springPop } from "../kinetics/spring.mjs";

export const LEVEL = Object.freeze({
  RING_A: [0.0, 0.3],    /* the share of the word in which the `from` ring draws, dash by dash */
  RULE: [0.12, 0.66],    /* ... the rule draws by length from `from` to the far end */
  RING_B: [0.58, 0.84],  /* ... the far ring draws as the rule arrives */
  LABEL: [0.7, 1.0],     /* ... and the label writes: it lands inside the word, never after it */
  PAD_PX: 14,            /* the air between a ring's edge and the label, in stage px */
  CLEAR_PX: 10,          /* how far the label's box keeps off the rule, in stage px (C14) */
  ASC: 0.8,              /* the label's box above its baseline, in its own size (a Kalam cap + its ascenders) */
  DESC: 0.22,            /* ... and below it */
  MID: 0.3,              /* a label written BESIDE a ring centres its x-height on the ring: the baseline this far down */
  RING_K: 0.55,          /* an end ring is the ring species' own round a point, at this scale: an END MARK (Bravos BUB 2:48 rings
                            each end small), never a callout - at 1.0 the far ring stood over the line's own end tag */
  OVERLAP: 1.6,          /* a glyph fades in over this many glyphs' share; the write is spread over n + OVERLAP - 1 shares so
                            the LAST letter finishes with the window (compare.mjs's law; R26-314: never half-inked) */
  FRAME_AIR_PX: 8,       /* where the page draws a plot frame, the label's box keeps this far inside its border, in stage px */
  SIDES: Object.freeze(["right", "left", "above", "below"]),
});

const lv01 = (v) => Math.min(1, Math.max(0, v));
const winF = (u, w) => lv01((u - w[0]) / Math.max(1e-6, w[1] - w[0]));

/* THE CLOCK at t: the draw fraction of each phase (0..1). `on` is false before the word. */
export const levelPose = (sp, t) => {
  const dur = Math.max(0.001, +sp.dur || 1), u = (t - +sp.at) / dur;
  return { on: u >= 0, ringA: winF(u, LEVEL.RING_A), rule: minJerk(winF(u, LEVEL.RULE)), ringB: winF(u, LEVEL.RING_B),
           label: winF(u, LEVEL.LABEL) };
};

/* one dash's own share of its ring's draw (the ring species' per-dash law, ringDashF, restated for a fraction `f`) */
export const levelDashF = (f, dash) => lv01((f - dash.t0) / Math.max(1e-6, dash.t1 - dash.t0));

/* each glyph's opacity for a write fraction `w` - the bracket's hand (a glyph fades in over OVERLAP of its own share),
   spread so the last glyph is whole exactly when w reaches 1 (compareGlyph's `per = 1 / (n + OVERLAP - 1)`) */
export const levelGlyphs = (w, n) => {
  const per = 1 / (Math.max(1, n) + LEVEL.OVERLAP - 1);
  return Array.from({ length: n }, (_, j) => lv01((w - j * per) / (per * LEVEL.OVERLAP)));
};

/* a ring dash's box round the origin, in the ring's own units (stage px): read once off its path ("M x y L x y ...") */
export const levelDashBox = (d) => {
  const n = String(d || "").replace(/[ML]/g, " ").trim().split(/\s+/).map(Number);
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (let j = 0; j + 1 < n.length; j += 2) { x0 = Math.min(x0, n[j]); x1 = Math.max(x1, n[j]); y0 = Math.min(y0, n[j + 1]); y1 = Math.max(y1, n[j + 1]); }
  return [x0, y0, x1, y1];
};

/* does a dash, its ring centred at P and scaled 1/k into the chart, stand on one of the page's words? */
export const levelDashYields = (box, P, k, words) => {
  const b = [P[0] + box[0] / k, P[1] + box[1] / k, P[0] + box[2] / k, P[1] + box[3] / k];
  return (words || []).some((w) => b[0] < w[2] && w[0] < b[2] && b[1] < w[3] && w[1] < b[3]);
};

/* THE RULE at a draw fraction: from A along the level to the far end's x. null when there is nothing to draw. */
export const levelRuleD = (A, E, f) => {
  if (!A || !E || !(f > 0)) return null;
  const x = A[0] + (E[0] - A[0]) * lv01(f);
  return "M" + A[0].toFixed(1) + " " + A[1].toFixed(1) + " L" + x.toFixed(1) + " " + A[1].toFixed(1);
};

/* the far end: the `to` datum, or - the axis form - the value axis at `from`'s own level */
export const levelFarEnd = (A, B, axisX) => (B ? B : (A && Number.isFinite(+axisX) ? [+axisX, A[1]] : null));

/* THE NUDGE into a plot frame: the (dx, dy) that moves `box` inside `frame` ([x0, y0, x1, y1], chart units) with `air`
   clear of its border - a box past the right or the top edge moves left / up, one past the left or the bottom right /
   down. `inside` is false when the box is wider or taller than the frame's room (it is then aligned left / top). */
export const levelNudge = (box, frame, air) => {
  if (!frame) return { dx: 0, dy: 0, inside: true };
  const a = +air || 0, fx0 = frame[0] + a, fy0 = frame[1] + a, fx1 = frame[2] - a, fy1 = frame[3] - a;
  let dx = 0, dy = 0;
  if (box[2] > fx1) dx = fx1 - box[2];
  if (box[0] + dx < fx0) dx = fx0 - box[0];
  if (box[1] < fy0) dy = fy0 - box[1];
  else if (box[3] > fy1) dy = fy1 - box[3];
  if (box[3] + dy > fy1 && box[1] + dy > fy0) dy = Math.max(fy0 - box[1], fy1 - box[3]);
  return { dx, dy, inside: box[2] - box[0] <= fx1 - fx0 + 1e-9 && box[3] - box[1] <= fy1 - fy0 + 1e-9 };
};

/* A LABEL'S BOX for one side of the far ring, in the chart's units: {x, y (baseline), anchor, box: [x0, y0, x1, y1],
   inside}. `g.frame` (the page's plot frame, or null) and `g.air` nudge it inside the frame (levelNudge). */
export const levelLabelAt = (side, E, g) => {
  const { rx, ry, pad, w, fs } = g, asc = fs * LEVEL.ASC, desc = fs * LEVEL.DESC, dy = (+g.dy || 0) * fs;
  let x, y, anchor;
  if (side === "right") { x = E[0] + rx + pad; y = E[1] + fs * LEVEL.MID; anchor = "start"; }
  else if (side === "left") { x = E[0] - rx - pad; y = E[1] + fs * LEVEL.MID; anchor = "end"; }
  else if (side === "above") { x = E[0]; y = E[1] - ry - pad - desc; anchor = "middle"; }
  else { x = E[0]; y = E[1] + ry + pad + asc; anchor = "middle"; }
  y += dy;
  const x0 = anchor === "start" ? x : anchor === "end" ? x - w : x - w / 2, box = [x0, y - asc, x0 + w, y + desc];
  const n = levelNudge(box, g.frame || null, g.air);
  return { side, x: x + n.dx, y: y + n.dy, anchor, box: [box[0] + n.dx, box[1] + n.dy, box[2] + n.dx, box[3] + n.dy], inside: n.inside };
};

const hit = (a, b) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];
const area = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));

/* THE RULE'S BAND: the box the label may never enter (C14) - the rule's x span at its level, CLEAR either side */
export const levelRuleBand = (A, E, clear) => [Math.min(A[0], E[0]), A[1] - clear, Math.max(A[0], E[0]), A[1] + clear];

/* is a label box ON the rule (C14)? */
export const levelOnRule = (box, A, E, clear) => hit(box, levelRuleBand(A, E, clear));

/* the cost of one placement: on the rule dominates, then the page's labels, the series' points, the chart's edge */
export const levelCost = (box, g) => {
  const band = levelRuleBand(g.A, g.E, g.clear);
  let c = hit(box, band) ? 1e6 + area(box, band) : 0;
  for (const b of g.boxes || []) if (hit(box, b)) c += 1e3 + area(box, b);
  for (const p of g.pts || []) if (p[0] >= box[0] && p[0] <= box[2] && p[1] >= box[1] && p[1] <= box[3]) c += 100;
  const W = g.W, H = g.H;
  if (Number.isFinite(W) && Number.isFinite(H)) {
    const out = Math.max(0, -box[0]) + Math.max(0, box[2] - W) + Math.max(0, -box[1]) + Math.max(0, box[3] - H);
    if (out > 0) c += 1e4 + out;
  }
  return c;
};

/* THE SIDE, decided once on the build's geometry: the authored one when there is one (s106), else the first clear
   side in the auto order - right, the gap's own side, the other, left - else the cheapest. `g` carries A, E, the ring
   radii, the pad, the label's width and size, the clear band, the page's label boxes, the series' points, W and H. */
export const levelSide = (g, authored) => {
  if (authored && LEVEL.SIDES.indexOf(authored) >= 0) return authored;
  const up = g.E[1] <= g.A[1];   /* the far datum stands at or over the rule (svg y grows down) */
  const order = ["right", up ? "above" : "below", up ? "below" : "above", "left"];
  let best = order[0], bestC = Infinity;
  for (const s of order) {
    const c = levelCost(levelLabelAt(s, g.E, g).box, g);
    if (c === 0) return s;
    if (c < bestC) { best = s; bestC = c; }
  }
  return best;
};

/* P72 T46d (R26-379; Bravos DOM 00:50.5 - the rule runs from the tip to the value axis and "4 %" stands there as a
   filled pill over the tick column, the "4" tick it covers gone; measured at 1280 px: the pill 46 x 32 round type 17 px
   tall where a tick is 12 - T9's axis pill law, AXTAG, handed in by the builder). `label_at: "axis"`: the pill POPS as
   the rule reaches the axis - from the label's window, on springPop over the builder's `pop.s` - and a tick label it
   covers is hidden while it stands. The pill's scale at t (0 before its instant): */
export const levelPillScale = (sp, t, pop) => {
  const dur = Math.max(0.001, +sp.dur || 1), d = t - (+sp.at + LEVEL.LABEL[0] * dur);
  if (!(d >= 0) || !pop) return 0;
  return springPop(lv01(d / Math.max(1e-6, +pop.s || 0.25)), +pop.mp || 0);
};

/* does the pill's rect ([x, y, w, h] at scale s about (cx, cy)) meet a tick's box [x, y, w, h]? */
export const levelPillHides = (cx, cy, box, s, tick) => {
  const w = s * box.w, h = s * box.h, x = cx - w / 2, y = cy - h / 2;
  return !!tick && w > 0 && h > 0 && x < tick[0] + tick[2] && tick[0] < x + w && y < tick[1] + tick[3] && tick[1] < y + h;
};

/* THE LEAVE: `lv` is the builder's {at, dur} of the undraw (or the replacing verb) that takes the line, or null (it stands) */
export const levelLeave = (lv, t) => (lv && Number.isFinite(+lv.at) ? minJerk(lv01((t - +lv.at) / Math.max(0.001, +lv.dur || 1))) : 0);

/* THE PAINTER (P71 T10). `sd` is the perform layer's built join: `g` (the group), `rule`, `ringA` / `ringB` ({g, dashes:
   [{p, t0, t1, box}]}), `words` (the page's own label boxes, [x0, y0, x1, y1], measured once by the builder), `label` +
   `lg` (its glyph tspans), the resolved `side`, the label geometry `lg0` ({rx, ry, pad, w, fs, dy}), the series `si`,
   the far end `to` ({si, i} or {axis: true}), `leave` (the verb that takes the line, or null), `k` (stage px per
   chart unit) and `frameOf(st)` (the active state's plot frame, [x0, y0, x1, y1], or null - a page with none).
   `ctx` is the PAGE species context: `datumNow` is lpDatumNow, handed in by name, so `node --test` calls this with
   recorders and no DOM; the builder's `sd.axisX(st)` is the active state's value-axis x (the axis form only). */
export const paintLevelJoin = (sd, t, st, ctx) => {
  const sp = sd.sp, pose = levelPose(sp, t), lv = levelLeave(sd.leave, t);
  const pill = sd.pill || null;
  const unhide = () => { if (!pill) return; for (const q of pill.hid || []) q.style.visibility = ""; pill.hid = []; };
  const hide = () => { sd.g.setAttribute("opacity", 0); if (pill) { pill.g.setAttribute("opacity", 0); unhide(); } };
  if (!pose.on || lv >= 1) { hide(); return; }
  const A = ctx.datumNow(st, sd.si, sp.from | 0);
  const B = sd.to.axis ? null : ctx.datumNow(st, sd.to.si, sd.to.i);
  const E = levelFarEnd(A, B, sd.to.axis && sd.axisX ? sd.axisX(st) : NaN);
  if (!A || !E) { hide(); return; }   /* R26-28: an end the window dropped joins nothing */
  sd.g.setAttribute("opacity", (1 - lv).toFixed(3));
  const d = levelRuleD(A, E, pose.rule);
  sd.rule.setAttribute("d", d || "M0 0");
  sd.rule.setAttribute("opacity", d ? 1 : 0);
  const ring = (R, P, f) => {
    R.g.setAttribute("transform", "translate(" + P[0].toFixed(1) + " " + P[1].toFixed(1) + ") scale(" + (1 / sd.k).toFixed(5) + ")");
    for (const dh of R.dashes) {
      const q = levelDashF(f, dh), off = dh.box && levelDashYields(dh.box, P, sd.k, sd.words);   /* a dash on the page's words stays undrawn */
      dh.p.setAttribute("stroke-dashoffset", (1 - q).toFixed(4));
      dh.p.setAttribute("opacity", q > 0 && !off ? 1 : 0);
    }
  };
  ring(sd.ringA, A, pose.ringA);
  ring(sd.ringB, E, pill ? 0 : pose.ringB);   /* R26-379: the axis pill stands where the far ring would */
  const at = levelLabelAt(sd.side, E, sd.frameOf ? Object.assign({}, sd.lg0, { frame: sd.frameOf(st) }) : sd.lg0);   /* the ACTIVE state's frame */
  sd.label.setAttribute("x", at.x.toFixed(1)); sd.label.setAttribute("y", at.y.toFixed(1));
  sd.label.setAttribute("text-anchor", at.anchor);
  const ops = levelGlyphs(pill ? 0 : pose.label, sd.lg.length);   /* the pill says the figure: the hand writes nothing */
  sd.lg.forEach((ts, j) => ts.setAttribute("opacity", ops[j].toFixed(3)));
  if (!pill) return;
  const s = levelPillScale(sp, t, pill.pop), cx = pill.colX(st), cy = A[1];
  unhide();
  if (!(s > 0)) { pill.g.setAttribute("opacity", 0); return; }
  pill.g.setAttribute("transform", "translate(" + cx.toFixed(1) + " " + cy.toFixed(1) + ") scale(" + s.toFixed(4) + ")");
  pill.g.setAttribute("opacity", (1 - lv).toFixed(3));
  for (const q of pill.ticksOf(st)) if (levelPillHides(cx, cy, pill.box, s, q.box)) { q.el.style.visibility = "hidden"; pill.hid.push(q.el); }
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.level_join = paintLevelJoin;
