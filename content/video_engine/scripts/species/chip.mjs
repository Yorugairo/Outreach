/* species/chip.mjs - THE ICON CHIP (P50 T2; doc 29 s9.27's motion menu; the Bravos icon board, shots 26-28:
   predictions land as chips and are crossed out one by one). SOURCE OF TRUTH, inlined into the scene-evidence
   player by sync_kinetics.py between KINETICS:BEGIN chip and KINETICS:END, AFTER spring and idle - it imports
   both, and the import order IS the region order.
   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the template's
   body. The last statement registers the painter in the template's SPECIES_PAINTERS registry; node, where no
   such registry exists, still imports the file for the pure math below.

   WHEN: the sentence names a THING as one of a SET (a prediction, an actor, a plant) - a chip lands on its
   word; a RETRACTS sentence ("none of this happened") crosses it out on a later word.

   THE LAW, all of it a pure function of t:
     land   - the badge spring (kinetics/spring.mjs springPop, the POP preset, Mp = 4 %) over LAND_S, from
              POP_FROM and DROP_PX above its place: R26-20's two-spring landing rides this one clock - the
              scale overshoots by Mp and settles, the drop rides the same x so the card never lands twice.
     hold   - opt-in `idle` (E49, one of IDLE_KINDS), applied exactly as the spotlight applies it: the idle's
              scale multiplies the landed scale, its offset moves the card, phased off the seed so two chips
              never breathe in step. Absent = declared stillness.
     cross  - `cross_at` draws a two-stroke X over the card by the template's drawOn (kinetics/stroke.mjs's
              curvature law when the flag is on, the species ease otherwise): the first stroke over the first
              half of CROSS_S, the second over the second, and the card dims to DIM as the X completes.
              `state: "crossed"` with no `cross_at` means the chip LANDS already crossed (the board is read
              back after the fact).
   Nothing is stored: every visual reads from t, sp.at and sp.cross_at, so a scrubbed frame is the played
   frame. The glyph is a SOURCED icon (assets/icons, A2a provenance) carried in the asset map as `icon:<name>`;
   this module never invents geometry. The dials below are ours to tune (42 s42.5), not findings. */
import { springPop } from "../kinetics/spring.mjs";
import { idleXf } from "../kinetics/idle.mjs";

export const CHIP = Object.freeze({
  SIZE: 168,        /* the card's side in STAGE px - a chip is read at a glance beside its neighbours, not studied */
  RX: 22,           /* the rounded corner (the dock card's 14px radius, scaled to the smaller card) */
  GLYPH: 92,        /* the glyph's box inside the card: a little over half the side, so the card reads as a card */
  LABEL_DY: 46,     /* the label's baseline below the card's bottom edge */
  LAND_S: 0.55,     /* the landing's wall clock - the dock's DOCK_POP_S 0.45 plus a beat: a chip is lighter than a card and travels further */
  POP_FROM: 0.82,   /* the scale it springs from (the dock's DOCK_POP_FROM is 0.85) */
  DROP_PX: 34,      /* ... and how far above its place it falls from, on the same spring */
  FADE_S: 0.14,     /* the opacity ramp, the dock's DOCK_FADE_S 0.12 - never a pop out of nothing */
  CROSS_S: 0.5,     /* the X's two strokes together */
  DIM: 0.55,        /* what a crossed chip dims to - struck through, still legible (it is still one of the set) */
});

const chip01 = (v) => Math.min(1, Math.max(0, v));

/* THE LANDING at t: the spring's normalised clock u, the scale it drives, the drop it rides and the fade. */
export const chipLand = (t, at, o = {}) => {
  const P = Object.assign({}, CHIP, o), u = chip01((t - at) / P.LAND_S), s = springPop(u);
  return { u, scale: P.POP_FROM + (1 - P.POP_FROM) * s, dy: (s - 1) * P.DROP_PX, fade: chip01((t - at) / P.FADE_S) };
};

/* THE CROSS at t in [0, 1]: 0 until cross_at, 1 CROSS_S later; a chip declared crossed is 1 from its landing. */
export const chipCrossF = (sp, t, o = {}) => {
  const P = Object.assign({}, CHIP, o);
  if (!Number.isFinite(+sp.cross_at)) return sp.state === "crossed" ? 1 : 0;
  return chip01((t - +sp.cross_at) / P.CROSS_S);
};

/* the two strokes of the X from the cross's fraction: the first over its first half, the second over the second */
export const chipStrokes = (f) => [chip01(f * 2), chip01(f * 2 - 1)];

/* ONE ENTRY: everything the painter draws at t, from the declaration alone. */
export const chipPose = (sp, t, o = {}) => {
  const P = Object.assign({}, CHIP, o), land = chipLand(t, +sp.at, P), cross = chipCrossF(sp, t, P);
  return { u: land.u, scale: land.scale, dy: land.dy, fade: land.fade,
           cross, strokes: chipStrokes(cross), dim: 1 - (1 - P.DIM) * cross };
};

/* the sourced icon's geometry as the compiler embedded it: {vb: [x, y, w, h], el: [{t, a}]}, or null. */
export const chipGeometry = (raw) => {
  if (typeof raw !== "string" || !raw) return null;
  try { const g = JSON.parse(raw); return Array.isArray(g && g.el) && g.el.length ? g : null; } catch (e) { return null; }
};

/* THE PAINTER. ctx is the template's species context (see SPECIES_PAINTERS in the player): the declaration,
   the clock, the layer and the shared helpers by name. Draws into one group whose transform carries the
   landing and the idle, so every child is written in the card's own centred coordinates. */
export function paintChip(ctx) {
  const { sp, t, svg, el, A, resolveTarget, drawOn, hash, idle, seed, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  const pose = chipPose(sp, t);
  const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 991)) : { scale: 1, dx: 0, dy: 0 };
  const cx = b.x + b.w / 2, cy = b.y + b.h / 2;   /* a point resolves to w = h = 0; a region centres the chip in it */
  const s = pose.scale * ix.scale;
  const g = el("g", "", svg, { opacity: pose.fade.toFixed(3),
                               transform: "translate(" + (cx + ix.dx).toFixed(1) + " " + (cy + pose.dy + ix.dy).toFixed(1) + ") scale(" + s.toFixed(4) + ")" });
  const body = el("g", "", g, { opacity: pose.dim.toFixed(3) });   /* the card dims under its own X; the X does not */
  const h = CHIP.SIZE / 2;
  el("rect", "chipcard", body, { x: (-h).toFixed(1), y: (-h).toFixed(1), width: CHIP.SIZE, height: CHIP.SIZE, rx: CHIP.RX });
  const geo = chipGeometry(A ? A["icon:" + sp.icon] : null);
  if (geo) {
    const vb = geo.vb || [0, 0, 24, 24], k = CHIP.GLYPH / Math.max(vb[2] || 1, vb[3] || 1);
    const gg = el("g", "chipglyph", body, { transform: "translate(" + (-CHIP.GLYPH / 2).toFixed(1) + " " + (-CHIP.GLYPH / 2).toFixed(1) + ") scale(" + k.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")" });
    geo.el.forEach((n) => el(n.t, "", gg, n.a));   /* the sourced geometry verbatim - the compiler already kept only shapes */
  }
  if (sp.label) {
    const lab = el("text", "chiplab", body, { x: 0, y: (h + CHIP.LABEL_DY).toFixed(1) });
    lab.textContent = sp.label;
  }
  if (pose.cross > 0) {   /* the two-stroke X, drawn by the curvature stroke over the card's diagonals */
    const a = CHIP.SIZE * 0.34;
    [["M" + (-a).toFixed(1) + " " + (-a).toFixed(1) + " L" + a.toFixed(1) + " " + a.toFixed(1), pose.strokes[0]],
     ["M" + a.toFixed(1) + " " + (-a).toFixed(1) + " L" + (-a).toFixed(1) + " " + a.toFixed(1), pose.strokes[1]]]
      .forEach(([d, f]) => { if (f > 0) drawOn(el("path", "sq", g, { d }), f); });
  }
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the template's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.chip = paintChip;
