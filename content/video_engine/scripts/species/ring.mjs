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
                   (species/flow.mjs flowDashes is the precedent; this is its ellipse). It ENCLOSES THE
                   DATUM'S OWN MARK: ink inside the ellipse's own x reach that stands clear ABOVE the
                   ellipse is part of the mark, and the ring is rebuilt round the box of the two - the same
                   pads, the same minima, the same hand (ringMark + ringHold; R26-67, read on the bridge
                   short's 69.0 s frame, where the line's last stretch spiked clear above the ring and the
                   ring then read as circling the air beside the apex). Ink that falls AWAY below the ring
                   is not the mark: a ring on a peak keeps the tight ellipse the peak was given.
     the flag    - optional, and a CHIP: the chip module's own card, sourced glyph and two-spring landing
                   (species/chip.mjs CHIP + chipLand + chipGeometry) placed beside the ellipse at FLAG_GAP off
                   its edge, FLAG_LAG after the ellipse closes. Its own dials are the chip's; this file only
                   says WHERE, and WHERE is the side with the ROOM: `flag_side` always wins; else a datum
                   inside the last FLAG_EDGE of the DRAWN SERIES' x extent flags LEFT and one inside the
                   first FLAG_EDGE flags right; and a card that would still cross either end of that extent
                   goes UNDER the ring, centred below the ellipse, rather than off the page (R26-67: on the
                   bridge short's 69.0 s frame the automatic choice took the side with no room and the card
                   was painted into the page's cream margin). With no extent to measure, the bound is the
                   stage's own edge - exactly the rule this file shipped with.
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
  FLAG_EDGE: 0.15,   /* the share at each END of the drawn series' x extent that has no room for a flag beside a datum in it (R26-67) */
  HUG_N: 24,         /* how many data either side of the datum the mark is LOOKED for in - a bound on the PROBES, never on the mark (the mark's bound is the ellipse's own rx): the bridge short's spike stands 23 data back from the datum R26-67 was read on */
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

/* PAST THE END OF ANY DRAWN SERIES. The engine CLAMPS a datum index to the series it actually drew - the
   exact-datum branch by Math.min(index, pts.length - 1), the bar branch by Math.min(index, bars.length - 1),
   the length-fraction fallback by clamp01 (resolveTarget, scene-evidence-engine.mjs) - so this is how the far
   end of the drawn data is ASKED for, rather than derived from a count this file does not have. */
const RING_PAST_END = 1 << 24;

/* THE DRAWN SERIES' X EXTENT in stage px, or null. It arrives the way every geometry in this file arrives:
   through the engine's own resolveTarget, on the SAME declared target with another index - the first datum,
   and one past the last. A target with no index (a point, a region, a caption word span) has no extent and
   takes null, which is the stage-edge rule this file shipped with. */
export const ringXExtent = (resolve, target) => {
  if (typeof resolve !== "function" || !target || !Number.isFinite(+target.index)) return null;
  const a = resolve(Object.assign({}, target, { index: 0 }));
  const b = resolve(Object.assign({}, target, { index: RING_PAST_END }));
  if (!a || !b) return null;
  const x0 = Math.min(a.x, b.x), x1 = Math.max(a.x + a.w, b.x + b.w);
  return x1 - x0 > 1 ? { x0, x1 } : null;
};

/* THE DATUM'S OWN MARK, a box in stage px (R26-67). A datum on a line resolves to a POINT, and the ink that
   runs through that point can stand OUTSIDE an ellipse drawn round the point alone: on the bridge short's
   69.0 s frame the line's last stretch spiked clear above the ring, and the ring read as a ring round the
   air beside the apex. So the mark is the datum AND any ink inside the ellipse's own x reach that stands
   clear ABOVE the ellipse - a ring encloses the ink it spans. Ink that falls AWAY under the ring (a peak's
   own shoulders, the drop after a top) is not this datum's mark and moves nothing, which is why a ring on a
   peak is untouched and only the rings that had ink towering over them change. THE ONE DIRECTION IS THE
   OPERATOR'S TO WIDEN: the mirror case - a datum in a trough with the ink plunging clear BELOW the ring -
   is left alone on purpose rather than guessed at (R26-67 was read on ink standing above).
   The ink is probed through the engine's resolveTarget, on the SAME declared target with a neighbour's
   index, so nothing here knows what a datum is: a target with no index never walks at all, and a target
   that resolves to a BOX (a bar) is its own mark already - a bar's neighbour is a DIFFERENT bar, and the
   pads are the hand's. HUG_N bounds the probes, e.rx bounds the mark, and a clamped repeat ends the walk
   where the drawn data does. */
export const ringMark = (b, e, resolve, target) => {
  let x0 = b.x, y0 = b.y, x1 = b.x + b.w, y1 = b.y + b.h;
  const box = () => ({ x: x0, y: y0, w: x1 - x0, h: y1 - y0 });
  if (b.w > 0 || b.h > 0 || typeof resolve !== "function" || !target || !Number.isFinite(+target.index)) return box();
  const i0 = +target.index | 0;
  for (const dir of [-1, 1]) {
    let prev = { x: b.x, y: b.y };
    for (let k = 1; k <= RING.HUG_N; k++) {
      const i = i0 + dir * k;
      if (i < 0) break;                                     /* an index before the first datum is not an index: never handed on */
      const q = resolve(Object.assign({}, target, { index: i }));
      if (!q || (q.x === prev.x && q.y === prev.y)) break;   /* nothing there, or the index clamped: the drawn data ends here */
      prev = q;
      if (Math.abs(q.x - e.cx) > e.rx) break;               /* past what the ellipse spans: that is the LINE, not this datum's mark */
      if (q.y >= e.cy - e.ry) continue;                     /* not standing clear above the ring: enclosed already, or falling away under it */
      x0 = Math.min(x0, q.x); x1 = Math.max(x1, q.x);
      y0 = Math.min(y0, q.y);
    }
  }
  return box();
};

/* THE ELLIPSE THAT HOLDS THE MARK: the SAME construction round the mark's box that the ring is built with
   round a datum's - the callout's own pads, the same minima - and then, if the box's corner is still outside
   it, grown by one factor so the aspect the pads gave it is kept and the dashes stay the dashes. A mark that
   IS the resolved target box (a bar, a region, a datum whose ink never left the ring) returns the ellipse it
   was handed, to the bit: the hand's own ring, untouched. */
export const ringHold = (e, mark, b, pad = 0) => {
  if (mark.x === b.x && mark.y === b.y && mark.w === b.w && mark.h === b.h) return e;
  const h = ringEllipse(mark, pad);
  const s = Math.hypot((mark.w / 2) / h.rx, (mark.h / 2) / h.ry);
  return s > 1 ? { cx: h.cx, cy: h.cy, rx: h.rx * s, ry: h.ry * s } : h;
};

/* WHERE the flag chip stands: beside the ellipse on the side that has the room - and UNDER it when neither
   side has any. `side` is the author's ("left" | "right") and always wins. Absent, the room is read off the
   DRAWN SERIES' x extent (`ext`, from ringXExtent): a datum inside the last FLAG_EDGE of it is asked for the
   LEFT first, one anywhere else for the right first, and a card whose own box would cross either end of that
   extent is refused that side. Refused both, the card goes UNDER the ellipse, centred, at the same FLAG_GAP:
   a lower card reads, a clipped one does not (R26-67). With no extent, the stage's edge decides - the rule
   this file shipped with, unchanged. */
export const ringFlagPlace = (e, side, stageW, ext = null) => {   /* stageW from the caller (the engine's STAGE_W): no landscape literal in player code (portrait parity) */
  const half = (CHIP.SIZE * RING.FLAG_K) / 2, gap = RING.FLAG_GAP + half;
  const at = (dir) => e.cx + dir * (e.rx + gap);
  if (side === "right" || side === "left") return { x: at(side === "right" ? 1 : -1), y: e.cy, side };
  if (ext) {
    const f = (e.cx - ext.x0) / Math.max(1e-6, ext.x1 - ext.x0);
    const fits = (dir) => at(dir) - half >= ext.x0 && at(dir) + half <= ext.x1;
    /* AT THE END OF THE SERIES THE LEFT IS TAKEN. The engine writes the series' own terminal tag just left of the
       last drawn point (s9.23b: the dense line's inline series name at its tip), and a stage painter cannot read
       the page's labels to dodge it - so the ring does not try: past the last FLAG_EDGE of the extent the flag
       goes UNDER the ellipse, into the plot's own empty room below the tip. Read on the frame this fix produced
       (build-short-axes 68.5 s, 2026-09-12): the chip had moved off the page's margin and onto the middle of
       "x3.9 Federal debt". The first FLAG_EDGE keeps the right, and everything between is the fit test. */
    if (f >= 1 - RING.FLAG_EDGE) return { x: e.cx, y: e.cy + e.ry + gap, side: "under" };
    for (const dir of [1, -1]) {
      if (fits(dir)) return { x: at(dir), y: e.cy, side: dir > 0 ? "right" : "left" };
    }
    return { x: e.cx, y: e.cy + e.ry + gap, side: "under" };
  }
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
  const e0 = ringEllipse(b, pad);   /* the ring the pads draw ... */
  const e = ringHold(e0, ringMark(b, e0, resolveTarget, sp.target), b, pad);   /* ... round the datum's own MARK (R26-67) */
  const pose = ringPose(sp, t);
  if (pose.f <= 0) return;
  const kind = sp.idle === "none" ? "none" : (sp.idle || "breath");
  const ix = kind === "none" ? { scale: 1, dx: 0, dy: 0 } : idle(kind, t, hash(seed | 0, si | 0, 991));
  const g = el("g", "", svg, { transform: "translate(" + (ix.dx + e.cx * (1 - ix.scale)).toFixed(2) + " " + (ix.dy + e.cy * (1 - ix.scale)).toFixed(2) + ") scale(" + ix.scale.toFixed(4) + ")" });
  ringDashes(e).forEach((dash) => {
    const f = ringDashF(pose.f, dash);
    if (f > 0) drawOn(el("path", "rngdash", g, { d: dash.d }), f);
  });
  const place = sp.flag ? ringFlagPlace(e, sp.flag_side, STAGE_W, ringXExtent(resolveTarget, sp.target)) : null;
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
