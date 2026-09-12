/* SPACE: stage */
/* species/countarray.mjs - THE ISOMETRIC COUNT ARRAY (P52 T7; EXPLORATION-REVIEW-2026-09-10.md:59, the Bravos
   reference at 7:43 - "the silos: a field of identical icons stacking up on a tilted plate"). SOURCE OF TRUTH,
   inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN countarray and KINETICS:END,
   AFTER spring, idle and chip - it imports all three, and the import order IS the region order.
   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the engine's body.
   The last statement registers the painter in SPECIES_PAINTERS; node, where no such registry exists, still
   imports the file for the pure math below.

   WHEN: the sentence COUNTS a set - "six plants", "twelve refineries", "three of them" - and the count itself
   is the claim. N identical icons stand on one tilted field and the number is written under them.

   THE LAW, all of it a pure function of t:
     the field  - a 2:1 RHOMBUS LATTICE and nothing else. Cell (c, r) stands at x = (c - r) * PITCH,
                  y = (c + r) * PITCH * RISE with RISE = 0.5 - the dimetric 2:1 step, so the lattice's two axes
                  read as one field and a row reads as a row. NO PERSPECTIVE CHEAT: no vanishing point, no
                  foreshortening with depth, no per-row scale - every icon is drawn at exactly one size, and the
                  only thing that says "back" is being higher up the field. NOTHING SPINS: no icon, tile or glyph
                  carries a rotation at any t (the test reads the painter's own attributes for one).
     arrive     - in READING ORDER (row 0 left to right, then row 1 ...), one icon per STEP - the take's own word
                  pitch - each landing on the CHIP's two-spring law (species/chip.mjs chipLand: the badge spring's
                  scale overshoot and the drop riding the same clock), so an icon in a field and a lone chip land
                  alike.
     the claim  - the COUNT, written under the field CLAIM_LAG after the last icon has landed, over CLAIM_S. The
                  compiler refuses a count that is not in the claim's own words
                  (build_scene_timeline_f._validate_count_array): the count IS the claim, never a caption of it.
     hold       - every cell carries the field's idle (E49, one of IDLE_KINDS; breath unless the row names
                  another), each at its OWN phase off the seed, so the field is never bit-identical frame to frame
                  and no two icons breathe in step. idle "none" is declared stillness.
   Nothing is stored: every visual reads from t, sp.at and sp.count, so a scrubbed frame is the played frame. The
   glyph is a SOURCED icon (assets/icons, A2a provenance - Lucide 1.45.0, ISC; assets/icons/SOURCES.md and
   LICENSE.lucide.txt beside it) carried in the asset map as icon:<name>; this module never invents geometry.
   The dials below are ours to tune (42 s42.5), not findings. */
import { springPop } from "../kinetics/spring.mjs";
import { idleXf } from "../kinetics/idle.mjs";
import { chipLand, chipGeometry } from "./chip.mjs";

export const COUNT = Object.freeze({
  MIN: 2,            /* a count of one is a chip; the compiler holds that bound, and the layout holds to it too */
  MAX: 12,           /* ... and past a dozen nobody counts a field at phone size - they read the number instead */
  PITCH: 190,        /* the lattice's half-width step in STAGE px: cell (c, r) is (c - r) * PITCH across ... */
  RISE: 0.5,         /* ... and (c + r) * PITCH * RISE down. 0.5 IS the 2:1 rhombus - the dimetric step, no perspective */
  ICON: 120,         /* the glyph's box: smaller than the chip's card, because a field is counted, not read one by one */
  TILE_K: 0.86,      /* the rhombus tile under an icon, as a share of the lattice's own cell - the tilted plate, seen */
  STEP: 0.34,        /* one icon per WORD [DERIVED: doc 46's take standard, 178 WPM = 0.337 s a word] */
  LAND_S: 0.45,      /* one icon's landing (the chip's 0.55 tightened: a field lands faster than a lone card) */
  POP_FROM: 0.86,    /* the scale it springs from ... */
  DROP_PX: 26,       /* ... and how far above its place it falls from, on the same spring */
  FADE_S: 0.12,      /* the opacity ramp - never a pop out of nothing */
  CLAIM_LAG: 0.18,   /* the breath between the last icon landing and the number being written ... */
  CLAIM_S: 0.4,      /* ... and the write's own clock */
  CLAIM_DY: 78,      /* the claim's baseline below the field's bottom edge */
  CLAIM_SIZE: 58,    /* ... at this size: the count is the claim, so it is the biggest type on the field */
  MIN_K: 0.4,        /* the smallest the field may be scaled to before it stops being counted - under it the box was too small */
});

const ca01 = (v) => Math.min(1, Math.max(0, v));
const CA_LAND = Object.freeze({ LAND_S: COUNT.LAND_S, POP_FROM: COUNT.POP_FROM, DROP_PX: COUNT.DROP_PX, FADE_S: COUNT.FADE_S });

/* THE LATTICE: N cells in READING ORDER - the columns of a row first, then the next row. The column count is the
   squarest field that holds N (ceil(sqrt(N))), so six stand 3 x 2 and nine 3 x 3. */
export const countCells = (n) => {
  const N = Math.max(1, Math.min(COUNT.MAX, n | 0)), cols = Math.max(1, Math.ceil(Math.sqrt(N))), out = [];
  for (let i = 0; i < N; i++) out.push({ i, c: i % cols, r: (i / cols) | 0 });
  return out;
};

/* THE FIELD in a declared box: each cell's centre in stage px, and the ONE scale the whole field is drawn at.
   The lattice is laid out at PITCH, measured, then scaled by that k and centred - so the 2:1 ratio survives any
   box, because a scale is not a perspective: both axes take the same k. */
export const countLayout = (box, n) => {
  const cells = countCells(n);
  const raw = cells.map((cell) => ({ i: cell.i, c: cell.c, r: cell.r,
                                     x: (cell.c - cell.r) * COUNT.PITCH, y: (cell.c + cell.r) * COUNT.PITCH * COUNT.RISE }));
  const xs = raw.map((p) => p.x), ys = raw.map((p) => p.y);
  const x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
  const y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
  const pad = COUNT.ICON * 0.5 + COUNT.PITCH * 0.1;
  const w = x1 - x0 + 2 * pad, h = y1 - y0 + 2 * pad + COUNT.CLAIM_DY;
  const k = Math.max(COUNT.MIN_K, Math.min(1, (box.w || w) / w, (box.h || h) / h));
  const cx = box.x + (box.w || 0) / 2, cy = box.y + (box.h || 0) / 2;
  const mx = (x1 + x0) / 2, my = (y1 + y0) / 2 + COUNT.CLAIM_DY / 2;
  return { k, w, h, claimY: cy + (y1 - my) * k + COUNT.CLAIM_DY * k,
           cells: raw.map((p) => ({ i: p.i, c: p.c, r: p.r, x: p.x, y: p.y,
                                    sx: cx + (p.x - mx) * k, sy: cy + (p.y - my) * k })) };
};

/* WHEN cell i arrives: its own word, STEP after the one before it. */
export const countArriveAt = (sp, i) => +sp.at + (i | 0) * (Number.isFinite(+sp.step) && +sp.step > 0 ? +sp.step : COUNT.STEP);

/* ONE CELL's landing at t - the CHIP's law under the field's dials, so a field and a board land alike. */
export const countCellPose = (sp, t, i) => chipLand(t, countArriveAt(sp, i), CA_LAND);

/* THE CLAIM's write at t in [0, 1]: 0 until CLAIM_LAG after the LAST icon has settled, 1 CLAIM_S later. */
export const countClaimF = (sp, t) => {
  const n = Math.max(1, Math.min(COUNT.MAX, (sp.count | 0)));
  const done = countArriveAt(sp, n - 1) + COUNT.LAND_S + COUNT.CLAIM_LAG;
  return ca01((t - done) / COUNT.CLAIM_S);
};

/* ONE ENTRY: everything the painter draws at t, from the declaration alone. */
export const countPose = (sp, t) => {
  const n = Math.max(1, Math.min(COUNT.MAX, (sp.count | 0)));
  const cells = [];
  for (let i = 0; i < n; i++) cells.push(countCellPose(sp, t, i));
  return { n, cells, landed: cells.filter((c) => c.u >= 1).length, claim: countClaimF(sp, t) };
};

/* the rhombus tile under one cell - the tilted plate, seen, in the cell's own centred coordinates. 2:1, like the
   lattice itself: the tile IS the lattice's cell, so the field reads as one plate and not as N floating icons. */
export const countTilePath = (k = 1) => {
  const a = COUNT.PITCH * COUNT.TILE_K * k, b = a * COUNT.RISE;
  return "M0 " + (-b).toFixed(1) + " L" + a.toFixed(1) + " 0 L0 " + b.toFixed(1) + " L" + (-a).toFixed(1) + " 0 Z";
};

/* the spring is the chip's, through chipLand; written out here so the test can assert the identity against
   springPop itself, and so a reader of one file sees which law lands an icon */
export const countSpring = (u) => COUNT.POP_FROM + (1 - COUNT.POP_FROM) * springPop(ca01(u));

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the clock,
   the layer and the shared helpers by name. One group per cell, its transform carrying the landing and the cell's
   own idle - so nothing rotates, and every child is written in the cell's centred coordinates. */
export function paintCountArray(ctx) {
  const { sp, t, svg, el, A, resolveTarget, ease, hash, idle, seed, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  const pose = countPose(sp, t), lay = countLayout(b, pose.n);
  const g = el("g", "", svg, {});
  const geo = chipGeometry(A ? A["icon:" + sp.icon] : null);
  const vb = geo ? (geo.vb || [0, 0, 24, 24]) : [0, 0, 24, 24];
  const ik = (COUNT.ICON * lay.k) / Math.max(vb[2] || 1, vb[3] || 1);
  const kind = sp.idle === "none" ? "none" : (sp.idle || "breath");
  lay.cells.forEach((cell, i) => {
    const p = pose.cells[i];
    if (p.fade <= 0) return;   /* an icon before its word is not on the field at all */
    const ix = kind === "none" ? { scale: 1, dx: 0, dy: 0 } : idle(kind, t, hash(seed | 0, (si | 0) * 31 + i, 991));
    const s = p.scale * ix.scale;
    const cg = el("g", "", g, { opacity: p.fade.toFixed(3),
                                transform: "translate(" + (cell.sx + ix.dx).toFixed(1) + " " + (cell.sy + p.dy * lay.k + ix.dy).toFixed(1) + ") scale(" + s.toFixed(4) + ")" });
    el("path", "catile", cg, { d: countTilePath(lay.k) });
    if (geo) {
      const gg = el("g", "caglyph", cg, { transform: "translate(" + (-COUNT.ICON * lay.k / 2).toFixed(1) + " " + (-COUNT.ICON * lay.k * 0.85).toFixed(1) + ") scale(" + ik.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")" });
      geo.el.forEach((nd) => el(nd.t, "", gg, nd.a));   /* the sourced geometry verbatim - the compiler kept only shapes */
    }
  });
  if (pose.claim > 0 && sp.claim) {   /* the count, written as the claim: a pop on its own clock, never a fade out of nothing */
    const pop = 0.72 + 0.28 * ease(pose.claim), cx = b.x + (b.w || 0) / 2;
    const tx = el("text", "caclaim", g, { x: cx.toFixed(1), y: lay.claimY.toFixed(1), opacity: pose.claim.toFixed(3),
                                          "font-size": (COUNT.CLAIM_SIZE * lay.k * pop).toFixed(1) });
    tx.textContent = sp.claim;
  }
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can import
   this file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.count_array = paintCountArray;
