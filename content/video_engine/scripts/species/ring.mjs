/* SPACE: stage */
/* species/ring.mjs - THE RING'S DASHED-ELLIPSE FORM, AND ITS FLAG CHIP (P52 T8;
   EXPLORATION-REVIEW-2026-09-10.md:57 #5 - "the dashed ellipse on the datum with a flag chip beside").
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN ring
   and KINETICS:END, AFTER spring, idle and chip - it imports all three, and the import order IS the region
   order.
   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the engine's
   body. The last statement registers the painter in SPECIES_PAINTERS; node, where no such registry exists,
   still imports the file for the pure math below.

   E56 IS NOT WIDENED BY THIS FILE. The operator, 2026-09-09: a ring circles a NUMBER or a POINT ON A CHART;
   a picture's focus is a LIGHT. What this module adds is a FORM - the dashed ellipse instead of the hand's
   closed circle - and an optional FLAG beside it. The USE is unchanged and is enforced where it always was,
   in the compiler (`build_scene_timeline_f._validate_ring`, which re-states `_validate_callout`'s own E56
   rule word for word): a datum target, or a label with a digit in it, or the row is refused at build time.
   The circle's law is untouched: the `callout` kind is still painted by the engine's own branch through
   `calloutPath`, with the same RX_PAD / RY_PAD this form rings the datum at, so the two forms ring the same
   place and only the hand differs.

   WHEN: the sentence TURNS on a number and the ring is wanted as a MARKER rather than as a hand's circle -
   a dashed ellipse round the datum, with a flag chip naming what the datum is.

   THE LAW, all of it a pure function of t:
     the ellipse - an axis-aligned ellipse round the resolved datum, rx = w/2 + RX_PAD, ry = h/2 + RY_PAD
                   (the callout's own pads, so the dashed form and the circle ring the same place), cut into
                   DASH-long marks with GAP between them and drawn DASH BY DASH clockwise from the top, each
                   dash owning its own slice of DRAW_S - the flow diagram's dashed frame, bent round a datum
                   (species/flow.mjs flowDashes is the precedent; this is its ellipse).
     the flag    - optional, and a CHIP: the chip module's own card, sourced glyph and two-spring landing
                   (species/chip.mjs CHIP + chipLand + chipGeometry) placed beside the ellipse at FLAG_GAP off
                   its right edge, FLAG_LAG after the ellipse closes. Its own dials are the chip's; this file
                   only says WHERE - and a chip on the LEFT when the ellipse's right edge would leave the
                   stage (`flag: "left"`, or measured against STAGE_W when the author says nothing).
     hold        - the ellipse and the flag carry a NAMED idle (E49, one of IDLE_KINDS; `breath` unless the
                   row names another), each at its own phase off the seed. NOTHING SPINS: no rotation is ever
                   written - a dash that turns is a wheel, and a wheel is the cheap call-out E56 refused.
   Nothing is stored: every visual reads from t and sp.at, so a scrubbed frame is the played frame. The dials
   below are ours to tune (42 s42.5), not findings. */
import { idleXf } from "../kinetics/idle.mjs";
import { CHIP, chipLand, chipGeometry } from "./chip.mjs";

export const RING = Object.freeze({
  FORM: "dashed",    /* the one form this module paints; the closed circle stays the `callout` kind's, untouched */
  RX_PAD: 22,        /* the ellipse's half-width over the datum's own box ... [the engine's calloutPath, verbatim] */
  RY_PAD: 18,        /* ... and its half-height: the dashed form rings exactly where the circle would */
  MIN_RX: 54,        /* a datum resolves to a POINT (w = h = 0): the smallest ellipse that still reads as a ring ... */
  MIN_RY: 40,        /* ... at the 4:3 the hand's circle draws round a bare datum */
  DASH: 26,          /* the dash's length in STAGE px ... [the flow diagram's frame, so one hand draws both] */
  DASH_GAP: 15,      /* ... and the air between two dashes: the 2:1 rhythm that reads as "dashed" */
  DRAW_S: 0.55,      /* the whole ellipse, dash by dash - the callout's CALLOUT_DRAW is 0.6; a dashed ring is quicker */
  SAMPLES: 10,       /* the polyline per dash: a dash is a short arc, and ten chords hide inside 26 px */
  ARC_SAMPLES: 720,  /* the arc-length table round the whole ellipse: half a degree a step, so a dash is cut by LENGTH */
  FLAG_GAP: 34,      /* the air between the ellipse's edge and the flag chip's card */
  FLAG_LAG: 0.14,    /* the breath after the ellipse closes before the flag lands */
  FLAG_K: 0.62,      /* the flag chip's scale against a board chip: a label on a datum, not a card in a set */
  LABEL_LIFT: 18,    /* how far above the ellipse the label is written when the flag has taken the room beside it */
});

const rg01 = (v) => Math.min(1, Math.max(0, v));
const LABEL_LIFT = RING.LABEL_LIFT;

/* THE ELLIPSE round a resolved target box, in stage px. A point resolves to w = h = 0 and takes the minimum. */
export const ringEllipse = (b, pad = 0) => ({
  cx: b.x + b.w / 2, cy: b.y + b.h / 2,
  rx: Math.max(RING.MIN_RX, b.w / 2 + RING.RX_PAD + pad),
  ry: Math.max(RING.MIN_RY, b.h / 2 + RING.RY_PAD + pad * 0.4),
});

/* the ellipse's perimeter, by Ramanujan's approximation - exact enough to cut dashes with (the error is
   under 1e-5 of the perimeter for every aspect a datum's box can take). */
export const ringPerimeter = (e) => {
  const a = Math.max(e.rx, e.ry), b = Math.min(e.rx, e.ry), h = Math.pow((a - b) / (a + b), 2);
  return Math.PI * (a + b) * (1 + 3 * h / (10 + Math.sqrt(4 - 3 * h)));
};

/* THE ARC-LENGTH TABLE: the ellipse sampled once, with the running length along it. An ellipse's equal ANGLES are
   NOT equal lengths (a bar's box rings as a tall ellipse, where a slice at the top covers a third of the arc a slice
   at the side does), so the dashes below are cut by LENGTH - the same thing the flow diagram's frame does on a
   rectangle. Pure: the table is a function of the ellipse alone. */
export const ringSamples = (e, m = RING.ARC_SAMPLES) => {
  const pts = [], cum = [0];
  for (let i = 0; i <= m; i++) {
    const a = -Math.PI / 2 + (i / m) * Math.PI * 2;
    pts.push([e.cx + Math.cos(a) * e.rx, e.cy + Math.sin(a) * e.ry]);
  }
  for (let i = 1; i <= m; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  return { pts, cum, per: cum[m] };
};

/* a distance along the ellipse -> the point there, by walking the table and interpolating inside one sample. */
export const ringPointAt = (tab, d) => {
  const per = tab.per, s = ((d % per) + per) % per;
  let lo = 0, hi = tab.cum.length - 1;
  while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (tab.cum[mid] <= s) lo = mid; else hi = mid; }
  const seg = Math.max(1e-9, tab.cum[hi] - tab.cum[lo]), u = (s - tab.cum[lo]) / seg;
  return [tab.pts[lo][0] + (tab.pts[hi][0] - tab.pts[lo][0]) * u,
          tab.pts[lo][1] + (tab.pts[hi][1] - tab.pts[lo][1]) * u];
};

/* THE DASHES: the ellipse cut BY LENGTH into marks of DASH with DASH_GAP between them, each with the slice of the
   whole draw it owns - the nib starts at the TOP and runs clockwise, the way a hand rings a number. Each dash is a
   short polyline, which is why the arc is sampled rather than swept: no rotation is ever written, and a dash never
   turns into the next one. The COUNT comes from the closed-form perimeter, the PLACES from the measured table. */
export const ringDashes = (e) => {
  const tab = ringSamples(e), n = Math.max(6, Math.round(ringPerimeter(e) / (RING.DASH + RING.DASH_GAP)));
  const step = tab.per / n, mark = step * (RING.DASH / (RING.DASH + RING.DASH_GAP));
  const out = [];
  for (let i = 0; i < n; i++) {
    const d0 = i * step, pts = [];
    for (let s = 0; s <= RING.SAMPLES; s++) pts.push(ringPointAt(tab, d0 + mark * (s / RING.SAMPLES)));
    out.push({ i, t0: i / n, t1: (i + 1) / n,
               d: pts.map(([x, y], j) => (j ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ") });
  }
  return out;
};

/* the whole ellipse's draw at t, 0..1 */
export const ringDrawF = (sp, t) => rg01((t - +sp.at) / RING.DRAW_S);

/* ... and one dash's own fraction inside it: 0 before the nib reaches it, 1 once it has passed. */
export const ringDashF = (f, dash) => rg01((f - dash.t0) / Math.max(1e-6, dash.t1 - dash.t0));

/* WHERE the flag chip stands: beside the ellipse, on the side that has the room. `side` is the author's
   ("left" | "right"), else the right unless the card would leave the stage. */
export const ringFlagPlace = (e, side, stageW) => {   /* stageW from the caller (the engine's STAGE_W): no landscape literal in player code (portrait parity) */
  const half = (CHIP.SIZE * RING.FLAG_K) / 2, gap = RING.FLAG_GAP + half;
  const right = side !== "left" && (side === "right" || e.cx + e.rx + gap * 2 <= stageW);
  return { x: e.cx + (right ? 1 : -1) * (e.rx + gap), y: e.cy, side: right ? "right" : "left" };
};

/* the flag's landing at t - the CHIP's own two-spring law, off the instant the ellipse closes. */
export const ringFlagPose = (sp, t) => chipLand(t, +sp.at + RING.DRAW_S + RING.FLAG_LAG, {});

/* ONE ENTRY: everything the painter draws at t, from the declaration alone. */
export const ringPose = (sp, t) => {
  const f = ringDrawF(sp, t);
  return { f, closed: f >= 1, flag: sp.flag ? ringFlagPose(sp, t) : null };
};

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the
   clock, the layer and the shared helpers by name. */
export function paintRing(ctx) {
  const { sp, t, svg, el, A, resolveTarget, drawOn, hash, idle, seed, si, STAGE_W } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  const pad = Number.isFinite(+sp.pad) ? +sp.pad : 0;
  const e = ringEllipse(b, pad), pose = ringPose(sp, t);
  if (pose.f <= 0) return;
  const kind = sp.idle === "none" ? "none" : (sp.idle || "breath");
  const ix = kind === "none" ? { scale: 1, dx: 0, dy: 0 } : idle(kind, t, hash(seed | 0, si | 0, 991));
  const g = el("g", "", svg, { transform: "translate(" + (ix.dx + e.cx * (1 - ix.scale)).toFixed(2) + " " + (ix.dy + e.cy * (1 - ix.scale)).toFixed(2) + ") scale(" + ix.scale.toFixed(4) + ")" });
  ringDashes(e).forEach((dash) => {
    const f = ringDashF(pose.f, dash);
    if (f > 0) drawOn(el("path", "rngdash", g, { d: dash.d }), f);
  });
  const place = sp.flag ? ringFlagPlace(e, sp.flag_side, STAGE_W) : null;
  if (sp.label) {   /* the ring's own label, where the engine's callout writes it: outside the ellipse, up and right -
       UNLESS the flag stands on that side, in which case it goes ABOVE the ellipse and starts at its left edge. A
       card that covers the number defeats the ring (read off the first frame of the `ring-dashed-chip` golden). */
    const right = !place || place.side === "left";
    const lx = right ? e.cx + e.rx + 12 : e.cx - e.rx, ly = e.cy - e.ry - (right ? 8 : LABEL_LIFT);
    const tx = el("text", "lab", g, { x: lx.toFixed(1), y: ly.toFixed(1), opacity: rg01(pose.f * 1.4).toFixed(3) });
    tx.textContent = sp.label;
  }
  if (!place || !pose.flag || pose.flag.fade <= 0) return;
  const fk = RING.FLAG_K * pose.flag.scale, h = CHIP.SIZE / 2;
  const fg = el("g", "", g, { opacity: pose.flag.fade.toFixed(3),
                              transform: "translate(" + place.x.toFixed(1) + " " + (place.y + pose.flag.dy).toFixed(1) + ") scale(" + fk.toFixed(4) + ")" });
  el("rect", "chipcard", fg, { x: (-h).toFixed(1), y: (-h).toFixed(1), width: CHIP.SIZE, height: CHIP.SIZE, rx: CHIP.RX });
  const geo = chipGeometry(A ? A["icon:" + sp.flag_icon] : null);
  if (geo) {
    const vb = geo.vb || [0, 0, 24, 24], k = CHIP.GLYPH / Math.max(vb[2] || 1, vb[3] || 1);
    const gg = el("g", "chipglyph", fg, { transform: "translate(" + (-CHIP.GLYPH / 2).toFixed(1) + " " + (-CHIP.GLYPH / 2).toFixed(1) + ") scale(" + k.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")" });
    geo.el.forEach((nd) => el(nd.t, "", gg, nd.a));   /* the sourced geometry verbatim - the compiler kept only shapes */
  }
  if (typeof sp.flag === "string" && sp.flag !== "on") {
    const lab = el("text", "chiplab", fg, { x: 0, y: (h + CHIP.LABEL_DY).toFixed(1) });
    lab.textContent = sp.flag;
  }
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.ring = paintRing;
