/* SPACE: page */
/* species/axis_tag.mjs - THE AXIS TAG and its DROP GUIDE (P71 T9, was P69 T38; the Bravos harvest v2's A10 "the named
   year / era / span replaces its tick as an accent pill", n=7, rank 3 - A42 / A43 are the same pill). SOURCE OF TRUTH,
   inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN axis_tag and KINETICS:END, AFTER
   ease, spring, span, lit_stretch and breakthrough (it imports all five, and the import order IS the region order).
   Its region sits BEFORE paintPerform, for span.mjs's reason: a PAGE species' painter is closed over by the perform
   layer, and a const has to exist before the function that closes over it is built.

   WHEN (`SPECIES_WHEN["axis_tag"]`, build_scene_timeline_f.py; BRAVOS-USE-WHEN.md:323): the sentence NAMES a year or
   an era ("in November of 1999", "the late 1990s") on a chart that carries it. Don't: the date is not spoken; more
   than 2-3 tags standing in one hold (the compiler WARNs a fourth with its numbers, E99 s106).

   THE LOOK, off Bravos's frames (HIS 05:50-05:54, JPN 01:16; BOOM "November 1999" 13:37): the tick's own label
   becomes a filled accent pill IN ITS PLACE - the same string, bolder - and a pill wider than one tick COVERS its
   neighbours. So the one rule here is: every x-axis label (an `xtick`, or a bars page's `xlabel`) whose box the pill
   overlaps is hidden while the pill stands - the NAMED one once the growing pill has swallowed it whole (the viewer
   sees the tick become the pill, as HIS 05:52 does), a neighbour the moment the pill's edge reaches it. The pill is
   the page's own callout capsule (`rect.cpill` + `text.callout`: the sunflower accent, the charcoal type, the one
   yellow the page has), so every gate that reads the callout reads this one.

   THE LAW, a pure function of t:
     the pop    - the pill springs in about its centre on springPop(Mp = POP_MP) over POP_S from the word (tippill's
                  named overshoot, R26-34); its text writes in only once the pill has covered the tick it names, so
                  the two strings never stand on each other (M28).
     the guide  - on a LINE page, a dotted rule drops from the datum the tag names down to the pill's top, drawn by
                  LENGTH on min-jerk from GUIDE_AT over GUIDE_S (the breakthrough capsule's dotted-leader law:
                  BREAK.CAP_LEAD_DASH / _W / _GAP - a solid rule across a chart is a comparator, E53 s6). It never
                  crosses one of the page's own labels (C14): the run is cut round every label box it would meet.
                  A bars page draws none (a guide down a bar is a seam in it - the capsule's own measured finding).
     the place  - re-read every frame on the ACTIVE state (R26-28): a line tag stands at its datum's live position
                  (the perform layer's datumNow, lerped across a rescale), a bars tag at its bar's; a value the active
                  state does not carry hides the tag rather than drawing it in the wrong place.
     the leave  - a tag is PAGE-BOUND (R26-219): a chart_to that replaces its page takes it on the page's own leave,
                  resolved by the compiler (`leave_at`), and the covered labels come back when it has gone.
   The dials are ours to tune (42 s42.5), not findings. */
import { minJerk } from "../kinetics/ease.mjs";
import { springPop } from "../kinetics/spring.mjs";
import { spanActiveState } from "./span.mjs";
import { litDrawnX } from "./lit_stretch.mjs";
import { BREAK } from "./breakthrough.mjs";

export const AXTAG = Object.freeze({
  POP_S: 0.25,        /* the pill's pop, from the word: a tick becoming a pill ARRIVES on the word, inside it */
  POP_MP: 0.05,       /* tippill's POP_MP - R26-34's named overshoot for a pill that arrives on a WORD */
  PAD_X: 14, PAD_Y: 9,/* tippill's TIPPILL.PAD_X / PAD_Y, BY VALUE: tippill's region sits after paintPerform, so a page module cannot import it (the node test pins them equal) */
  RADIUS: 12,         /* tippill's pillBox corner: min(h / 2, 12) */
  TYPE_K: 1.25,       /* the pill's type over the tick's own: the template's .callout (30) over .lab (24), the page's one capsule ratio */
  GUIDE_AT: 0.1,      /* the guide starts this far into the word (the pill is half popped) ... */
  GUIDE_S: 0.28,      /* ... and drops by length over this: pill and guide have both landed 0.38 s after the word */
  GUIDE_GAP: BREAK.CAP_LEAD_GAP,     /* the guide stops this short of the datum and of the pill: it points, it does not touch */
  GUIDE_DASH: BREAK.CAP_LEAD_DASH,   /* ... dotted */
  GUIDE_W: BREAK.CAP_LEAD_W,         /* ... at the leader's weight */
  LABEL_PAD: 6,       /* C14: the guide stops this far short of a label box it would cross */
  RULE_S: 0.5,        /* P72 T53 (i) / R26-415: `guide: "rule"` - the DATED RULE drops the plot's full height over this ... */
  RULE_DASH: "10 8",  /* ... DASHED, Bravos's projected-date rule (BOOM 18:00.5), not the datum leader's dots */
  MAX_STANDING: 3,    /* the don't (USE-WHEN :323): "more than 2-3 tags in one hold" - build_scene_timeline_f.AXIS_TAG_MAX, the compiler's copy */
});

const ax01 = (v) => Math.min(1, Math.max(0, v));

/* THE POSE at t: is it up, the pop's scale (springPop overshoots, then 1), the guide's drawn share (0..1). `t0` is
   when the clock starts (axtagStart: the word, or the instant its page has arrived); absent, the word. */
export const axtagPose = (sp, t, t0) => {
  const d = t - (Number.isFinite(t0) ? t0 : (+sp.at || 0));
  if (!(d >= 0)) return { on: false, s: 0, u: 0, guide: 0 };
  const u = ax01(d / AXTAG.POP_S);
  return { on: true, u, s: springPop(u, AXTAG.POP_MP), guide: minJerk(ax01((d - AXTAG.GUIDE_AT) / AXTAG.GUIDE_S)),
           rule: minJerk(ax01((d - AXTAG.GUIDE_AT) / AXTAG.RULE_S)) };
};

/* WHEN THE POP STARTS: on its word - unless its word falls while the chart state it names is still ARRIVING. A state
   stands (the one a species resolves against) only when the chart_to that brings it in has run (the engine's
   lpPaintStates: a recast hands over for its `dur` - a keyed "data" recast for at least `keyedMin` - and only then is
   the new state the active one). A pill that popped under the hand-over would appear WHOLE at the switch, so the pop
   waits for it: the last state-changing chart_to at or before the word, and its end. A pure function of the row. */
const AXTAG_STILL = Object.freeze(["park", "compare"]);   /* verbs that change no state */
export const axtagStart = (sp, chartTos, keyedMin = 0) => {
  const at = +sp.at || 0;
  let end = -Infinity;
  for (const c of chartTos || []) {
    if (!c || AXTAG_STILL.indexOf(c.to) >= 0 || !(+c.at <= at + 1e-9)) continue;
    const d = Math.max(0.001, +c.dur || 1);
    end = +c.at + (c.keyed === "data" ? Math.max(d, keyedMin) : d);
  }
  return Math.max(at, end);
};

/* the pill's box for a measured text width and height - tippill's pillBox shape, about its centre */
export const axtagPillBox = (w, h) => {
  const bw = w + 2 * AXTAG.PAD_X, bh = h + 2 * AXTAG.PAD_Y;
  return { w: bw, h: bh, x: -bw / 2, y: -bh / 2, r: Math.min(bh / 2, AXTAG.RADIUS) };
};

/* the pill's rect at scale s about (cx, cy), as [x, y, w, h] */
export const axtagRect = (cx, cy, pill, s) => [cx - (s * pill.w) / 2, cy - (s * pill.h) / 2, s * pill.w, s * pill.h];
export const axtagOverlaps = (a, b) => !!a && !!b && a[2] > 0 && a[3] > 0 && b[2] > 0 && b[3] > 0
  && a[0] < b[0] + b[2] && b[0] < a[0] + a[2] && a[1] < b[1] + b[3] && b[1] < a[1] + a[3];
export const axtagContains = (a, b) => !!a && !!b && a[0] <= b[0] && a[1] <= b[1] && a[0] + a[2] >= b[0] + b[2] && a[1] + a[3] >= b[1] + b[3];
/* the covering rule: the NAMED tick hides once the pill contains it (the tick becomes the pill), a neighbour the moment
   the pill's edge reaches it (the pill covers it) */
export const axtagHides = (rect, box, named) => (named ? axtagContains(rect, box) : axtagOverlaps(rect, box));
/* the scale at which the pill about (cx, cy) contains a box: its text may write from here on */
export const axtagCoverScale = (cx, cy, pill, box) => {
  if (!box) return 0;
  const sx = (2 * Math.max(cx - box[0], box[0] + box[2] - cx)) / Math.max(1e-6, pill.w);
  const sy = (2 * Math.max(cy - box[1], box[1] + box[3] - cy)) / Math.max(1e-6, pill.h);
  return Math.max(0, sx, sy);
};

/* C14: the guide's runs down x from y0 to y1, cut round every label box it would cross (padded by `pad`). Sorted,
   never empty-length; [] when the labels take all of it. */
export const axtagGuideRuns = (x, y0, y1, boxes, pad = AXTAG.LABEL_PAD) => {
  if (!(y1 > y0)) return [];
  const cuts = [];
  for (const b of boxes || []) {
    if (!b || !(x >= b[0] - pad && x <= b[0] + b[2] + pad)) continue;
    const a = b[1] - pad, z = b[1] + b[3] + pad;
    if (z > y0 && a < y1) cuts.push([Math.max(y0, a), Math.min(y1, z)]);
  }
  cuts.sort((p, q) => p[0] - q[0]);
  const runs = [];
  let y = y0;
  for (const [a, z] of cuts) { if (a > y) runs.push([y, a]); y = Math.max(y, z); }
  if (y < y1) runs.push([y, y1]);
  return runs.filter(([a, z]) => z - a > 0.5);
};

/* the runs drawn DOWN to `to` (the guide drops from the datum), as one path of sub-paths */
export const axtagGuideD = (x, runs, to) => runs
  .filter(([a]) => a < to)
  .map(([a, z]) => "M" + x.toFixed(1) + " " + a.toFixed(1) + " L" + x.toFixed(1) + " " + Math.min(z, to).toFixed(1))
  .join(" ");

/* a label's box THIS FRAME: its build-time size about its LIVE x (a rescale moves the ticks; their size does not) */
export const axtagLabelBox = (lab) => {
  const x = parseFloat(lab.el.getAttribute("x"));
  if (!Number.isFinite(x)) return null;
  const x0 = lab.anchor === "middle" ? x - lab.w / 2 : lab.anchor === "end" ? x - lab.w : x;
  return [x0, lab.top, lab.w, lab.h];
};

/* WHERE the tag stands this frame, on the ACTIVE state: {x, y (the datum's, or null), cy (the tick row's centre),
   named (the label it names, or null), S} - or null when the active state does not carry the value (R26-28) */
export const axtagPlace = (td, st, ctx) => {
  const S = spanActiveState(st), k = (st && st.states && st.states.length > 1) ? (st.active | 0) : 0;
  const on = (td.on || [])[k];
  if (!on) return null;
  const p = on.di == null ? null : ctx.datumNow(st, on.si, on.di);
  if (on.di != null && !p) return null;
  const named = on.label || null, nb = named ? axtagLabelBox(named) : null;
  const x = p ? p[0] : nb ? nb[0] + nb[2] / 2 : null;
  if (x == null || !Number.isFinite(on.cy)) return null;
  return { x, y: on.bars || !p ? null : p[1], cy: on.cy, named, S, si: on.si, k, top: on.top, bars: !!on.bars };
};

/* P72 T53 (i) / R26-415 - THE DATED RULE (Bravos A56, BOOM 18:00.5: a full-height dashed rule at the projected date, its
   pill on the axis). `guide: "rule"` drops from the PLOT's top (the state's own, `on.top`) to the pill's top - it hangs
   from the date, not from a datum, so a date the page carries only as a tick (the estimate's, which E77 refuses as data)
   gets its rule. Top-down by length on min-jerk over RULE_S, cut round the page's labels (C14). A bars page draws none. */
const axtagRuleD = (P, td, pose, boxes) => {
  if (P.bars || !Number.isFinite(P.top)) return "";
  const y1 = P.cy - td.pill.h / 2 - AXTAG.GUIDE_GAP;
  return axtagGuideD(P.x, axtagGuideRuns(P.x, P.top, y1, boxes), P.top + (y1 - P.top) * pose.rule);
};

/* THE PAINTER (P71 T9). `at` is the perform layer's built set - `tags` (each: `sp`, the pill group `g`, `rect`,
   `text`, `guide`, the measured `pill` box, its clock's start `t0` (axtagStart), and `on[k]` per chart state: the datum it names, the label it names and
   the row's centre), `labels` (every x-axis label of every state: `el`, its build-time `w` / `h` / `top` / `anchor`)
   `boxesOf[k]` (state k's own label boxes, the guide's C14 obstacles) and `leaveOf(sp, t)` (the engine's pageLeave;
   absent in a test). `ctx` is the page species context. */
export const paintAxisTags = (at, t, st, ctx) => {
  const hide = new Set();
  for (const td of at.tags || []) {
    const pose = axtagPose(td.sp, t, td.t0), lv = at.leaveOf ? at.leaveOf(td.sp, t) : 0;
    const P = pose.on && lv < 1 ? axtagPlace(td, st, ctx) : null;
    if (!P) { td.g.setAttribute("opacity", 0); td.guide.setAttribute("opacity", 0); continue; }
    const s = Math.max(0, pose.s), rect = axtagRect(P.x, P.cy, td.pill, s);
    td.g.setAttribute("transform", "translate(" + P.x.toFixed(1) + " " + P.cy.toFixed(1) + ") scale(" + s.toFixed(4) + ")");
    td.g.setAttribute("opacity", (1 - lv).toFixed(3));
    const nb = P.named ? axtagLabelBox(P.named) : null, sc = axtagCoverScale(P.x, P.cy, td.pill, nb);
    const said = pose.u >= 1 ? 1 : ax01((s - sc) / Math.max(1e-6, 1 - sc));
    td.text.setAttribute("opacity", said.toFixed(3));
    for (const lab of at.labels || []) {
      const b = axtagLabelBox(lab);
      if (b && axtagHides(rect, b, lab === P.named)) hide.add(lab);
    }
    /* R26-415: ONE PRINT - a page label writing the pill's own string (an estimate's end tag "2026E") yields while the
       pill's text stands: the date is said once, on the axis */
    if (said > 0) for (const dp of td.dupes || []) hide.add(dp);
    if (td.sp.guide === "rule") {
      const d = axtagRuleD(P, td, pose, (at.boxesOf || [])[P.k] || []);
      td.guide.setAttribute("d", d);
      td.guide.setAttribute("opacity", d ? (1 - lv).toFixed(3) : 0);
      continue;
    }
    /* the guide: a line page's, from the datum down to the pill's top, cut round the page's labels, never ahead of the ink */
    const drawn = P.y == null ? null : litDrawnX((P.S && P.S.paths) || [], P.si);
    if (P.y == null || td.sp.guide === false || drawn === null || drawn < P.x - 0.5) { td.guide.setAttribute("opacity", 0); continue; }
    const y0 = P.y + AXTAG.GUIDE_GAP, y1 = P.cy - td.pill.h / 2 - AXTAG.GUIDE_GAP;
    const runs = axtagGuideRuns(P.x, y0, y1, (at.boxesOf || [])[P.k] || []);
    const d = axtagGuideD(P.x, runs, y0 + (y1 - y0) * pose.guide);
    td.guide.setAttribute("d", d);
    td.guide.setAttribute("opacity", d ? (1 - lv).toFixed(3) : 0);
  }
  /* the covered labels, re-decided every frame from t alone: hidden while a pill covers them, given back after */
  for (const lab of [...(at.labels || []), ...(at.tags || []).flatMap((td) => td.dupes || [])]) {
    if (hide.has(lab)) { lab.el.style.visibility = "hidden"; lab.hid = true; }
    else if (lab.hid) { lab.el.style.visibility = ""; lab.hid = false; }
  }
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.axis_tag = paintAxisTags;
