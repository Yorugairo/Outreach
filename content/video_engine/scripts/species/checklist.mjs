/* species/checklist.mjs - THE TEST CARD (P55 T7; the chart dock's `checklist` form, CHECKLIST v2 - typewriter +
   marker-highlight, technique ported from remotion-ui: cap-height band, chisel-tilt leading edge, ~0.3 ink over dark
   ground). SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN
   checklist and KINETICS:END, AFTER ink - it imports kmHex and INK, and the import order IS the region order.

   A CHART-DOCK FORM, not a species kind: this module registers NO painter. The engine's chart build calls
   buildChecklist and its drawChart calls paintChecklist by name (P55 T7: no new registry). Promoted from inline
   engine code with every frame byte-identical (the golden `test-card`): each literal below is the value the inline
   code carried.

   WHEN (the checklist v2 comment in the engine): a question is put to several candidates - rows whose question cells
   TYPE on and whose answer cells get the highlighter swept through them; optional per-row cell colours (r.colors)
   make it a status board.

   THE LAW, all of it a pure function of the dock's clock tRel except the one-time column fit (which needs the DOM):
     fit    - QC 2026-08-30: columns AUTO-FIT. Natural width per column (headers and cells, col 0 measured with its
              full text), distributed across the usable span; slack spreads evenly, a deficit squeezes proportionally,
              and an over-long cell compresses via textLength.
     rows   - row i lands at its `delay` (else i * ROW_DELAY_S); a checklist on a hold under RECAP_S is a RECAP and
              fills fast (ri * RECAP_ROW_S) - QC 2026-08-30, the s73 scorecard showed EMPTY.
     cells  - inside a row: the question TYPES at +0 (one char per TYPE_S), the next cell fades at +0.6, the answers
              sweep at +1.0 and +1.6 (OFFS; RECAP_OFFS on a recap); each cell fades in over CELL_FADE_S.
     sweep  - the band is cap-height, behind the text, clipped by a chisel-tilted wipe that grows on an out-cubic over
              SWEEP_S; the skew pivots about the BAND'S OWN corner (a bare skewX pivots about the SVG origin and
              amputates the highlight's right end - the "incomplete highlighter" QC class).
   The dials below are ours to tune (42 s42.5), not findings. */
import { INK, kmHex } from "../kinetics/ink.mjs";

export const CHECKLIST = Object.freeze({
  COLORS: Object.freeze(["#f4f6f8", "#dce3ea", "#3bc9b0", "#ff8a8c"]),   /* the default column colours: question, detail, steel, paper */
  HEAD_DY: 18,           /* the header row's baseline below the plot top */
  ROW0_DY: 64,           /* the first row's baseline below the plot top ... */
  ROW_PITCH: 58,         /* ... and the row pitch */
  ROW_DELAY_S: 3,        /* a row with no `delay` lands at i * this */
  HL_FROM_COL: 2,        /* cells from this column on carry the highlighter band */
  BAND_INSET: 8,         /* the band starts this far left of its column ... */
  BAND_RISE: 21,         /* ... and this far above the baseline ... */
  BAND_H: 30,            /* ... cap-height tall ... */
  BAND_W0: 10,           /* ... at this initial width ... */
  BAND_RX: 4,            /* ... with this corner radius ... */
  BAND_ALPHA: 0.28,      /* ... at this ink alpha (without the K-M flag) */
  KM_GROUND: "#16181c",  /* the dark ground the K-M band is a layer of ink over (44 s44.1) */
  RULE_DY: 18,           /* the row rule below the baseline ... */
  RULE_COLOR: "#24262b", /* ... its colour ... */
  RULE_W: 1.5,           /* ... and its stroke width */
  FIT_MARGIN: 28,        /* the usable span = CW - PL - this */
  FIT_MIN_W: 40,         /* a column's natural width floor */
  FIT_PAD: 26,           /* the padding added to every column's natural width */
  FIT_CHAR_W: 10,        /* the width per character when the DOM cannot measure */
  FIT_X0: 64,            /* the first column's x */
  FIT_ROOM_SLACK: 8,     /* a cell's room = its allotment - FIT_PAD + this */
  CHISEL_DEG: -7,        /* the wipe's chisel tilt (skewX) */
  RECAP_S: 12,           /* a hold shorter than this is a RECAP */
  RECAP_ROW_S: 0.8,      /* the recap's row step */
  OFFS: Object.freeze([0, 0.6, 1.0, 1.6]),          /* the cell offsets inside a row: types, fades, steel sweep, paper sweep */
  RECAP_OFFS: Object.freeze([0, 0.25, 0.45, 0.7]),  /* ... and on a recap */
  CELL_FADE_S: 0.35,     /* each cell's fade-in */
  TYPE_S: 0.045,         /* the type-on rate: one character per this */
  SWEEP_S: 0.55,         /* the highlighter's sweep clock (out-cubic) */
  SWEEP_W_FALLBACK: 300, /* the text width (and room) when the DOM cannot measure */
  SWEEP_PAD: 18,         /* the sweep runs this past the text ... */
  SWEEP_ROOM_PAD: 12,    /* ... capped at the cell's room plus this */
});

const checklist01 = (v) => Math.min(1, Math.max(0, v));

/* row i's baseline from the plot top */
export const checklistRowY = (pt, i, V = CHECKLIST) => pt + V.ROW0_DY + i * V.ROW_PITCH;

/* is the hold a recap? */
export const checklistRecap = (d, V = CHECKLIST) => (d.exit - d.enter) < V.RECAP_S;

/* row ri's delay: its declared one (r.d), or the recap's fast step */
export const checklistRowDelay = (r, ri, recap, V = CHECKLIST) => recap ? ri * V.RECAP_ROW_S : r.d;

/* cell k's clock inside its row */
export const checklistCellClock = (tRel, rowDelay, k, recap, V = CHECKLIST) => {
  const offs = recap ? V.RECAP_OFFS : V.OFFS;
  return tRel - rowDelay - offs[Math.min(k, 3)];
};

/* the number of characters typed at the cell's clock */
export const checklistTyped = (ct, V = CHECKLIST) => Math.max(0, Math.floor(ct / V.TYPE_S));

/* the highlighter's sweep fraction at the cell's clock */
export const checklistSweep = (ct, V = CHECKLIST) => {
  const p = checklist01(ct / V.SWEEP_S);
  return 1 - Math.pow(1 - p, 3);
};

/* THE COLUMN FIT from the natural widths: allotments, the squeeze, the spread slack and each column's x */
export const checklistColumns = (natW, usable, V = CHECKLIST) => {
  const NC = natW.length;
  const alloc = natW.map((w) => w + V.FIT_PAD);
  const total = alloc.reduce((a, b) => a + b, 0);
  const scale2 = total > usable ? usable / total : 1;
  const extra = total < usable ? (usable - total) / NC : 0;
  const xs = []; let acc = V.FIT_X0;
  for (let ci = 0; ci < NC; ci++) {
    xs.push(acc); acc += alloc[ci] * scale2 + extra;
  }
  return { alloc, scale2, extra, xs };
};

/* THE BUILD, inside the chart build: ctx = { mk, slot, PL, PT, CW, PR, kin } from the engine's chart scope.
   Returns { rowEls, chkFit } for the chart state. */
export function buildChecklist(spec, ctx, V = CHECKLIST) {
  const { mk, slot, PL, PT, CW, PR, kin } = ctx;
  const headEls = spec.head.map((h) =>
    mk("text", { class: "csr", x: PL, y: PT + V.HEAD_DY }, h));
  const rowEls = [];
  spec.rows.forEach((r, i) => {
    const y = checklistRowY(PT, i, V);
    const colr = r.colors || V.COLORS;
    const cells = [];
    r.cells.forEach((cell, ci) => {
      const g2 = mk("g", { opacity: 0 });
      let sweep = null, band = null;
      if (ci >= V.HL_FROM_COL && cell) {
        const cid2 = "hl" + slot + i + ci;
        const cp2 = mk("clipPath", { id: cid2 }, null,
                       mk("defs", {}, null, g2));
        sweep = mk("rect", { x: PL - V.BAND_INSET, y: y - V.BAND_RISE,
          width: 0, height: V.BAND_H }, null, cp2);
        const kmBand = kin("km_ink") && /^#[0-9a-f]{6}$/i.test(colr[ci]);   /* K-M (44 s44.1): the band IS a layer of ink over the ground */
        band = mk("rect", { x: PL - V.BAND_INSET, y: y - V.BAND_RISE, width: V.BAND_W0,
           height: V.BAND_H, rx: V.BAND_RX, fill: kmBand ? kmHex(V.KM_GROUND, colr[ci], INK.HIGHLIGHT_X) : colr[ci], opacity: kmBand ? 1 : V.BAND_ALPHA,
           "clip-path": `url(#${cid2})`, class: "hlband" + slot + i + ci }, null, g2);
      }
      const tx = mk("text", { class: "cs", x: PL, y,
         fill: colr[ci] }, ci === 0 ? "" : cell, g2);
      cells.push({ el: g2, tx, txt: cell, ci, sweep, band, y,
                   bandCls: "hlband" + slot + i + ci });
    });
    mk("line", { x1: PL, x2: CW - PR, y1: y + V.RULE_DY, y2: y + V.RULE_DY,
       stroke: V.RULE_COLOR, "stroke-width": V.RULE_W });
    rowEls.push({ d: r.delay || i * V.ROW_DELAY_S, cells, y });
  });
  return { rowEls, chkFit: { headEls, done: false, usable: CW - PL - V.FIT_MARGIN } };
}

/* the one-time column fit - measurement needs the DOM */
const fitChecklist = (st, V) => {
  const F = st.chkFit, NC = F.headEls.length, PAD = V.FIT_PAD;
  const natW = new Array(NC).fill(V.FIT_MIN_W);
  const meas = (el) => el.getComputedTextLength
    ? el.getComputedTextLength() : (el.textContent.length * V.FIT_CHAR_W);
  F.headEls.forEach((h, ci) => natW[ci] = Math.max(natW[ci], meas(h)));
  for (const r of st.rowEls) for (const c of r.cells) {
    const keep = c.tx.textContent;
    if (c.ci === 0) c.tx.textContent = c.txt;
    natW[c.ci] = Math.max(natW[c.ci], meas(c.tx));
    if (c.ci === 0) c.tx.textContent = keep;
  }
  const { alloc, scale2, extra, xs } = checklistColumns(natW, F.usable, V);
  F.headEls.forEach((h, ci) => h.setAttribute("x", xs[ci]));
  for (const r of st.rowEls) for (const c of r.cells) {
    c.tx.setAttribute("x", xs[c.ci]);
    const room = alloc[c.ci] * scale2 + extra - PAD + V.FIT_ROOM_SLACK;
    if (c.ci > 0 && natW[c.ci] >= room && meas(c.tx) > room) {
      c.tx.setAttribute("textLength", room.toFixed(0));
      c.tx.setAttribute("lengthAdjust", "spacingAndGlyphs");
    }
    c.room = room;
    if (c.sweep) {
      const x0 = xs[c.ci] - V.BAND_INSET, y0 = c.y - V.BAND_RISE;
      for (const el of [c.sweep, c.band]) {
        el.setAttribute("x", x0); el.setAttribute("y", y0);
      }
      c.sweep.setAttribute("transform",
        `translate(${x0} ${y0}) skewX(${V.CHISEL_DEG}) translate(${-x0} ${-y0})`);
    }
  }
  F.done = true;
};

/* THE PAINTER, inside drawChart on the dock's clock tRel: the one-time fit, then every row's cells. */
export function paintChecklist(st, tRel, d, V = CHECKLIST) {
  if (st.chkFit && !st.chkFit.done && st.rowEls && st.rowEls.length) fitChecklist(st, V);
  const recap = checklistRecap(d, V);
  (st.rowEls || []).forEach((r, ri) => {
    const rowDelay = checklistRowDelay(r, ri, recap, V);
    r.cells.forEach((c, k) => {
      const ct = checklistCellClock(tRel, rowDelay, k, recap, V);
      const o = checklist01(ct / V.CELL_FADE_S);
      c.el.setAttribute("opacity", o.toFixed(2));
      if (c.ci === 0) {
        const want = c.txt.slice(0, checklistTyped(ct, V));
        if (c.tx.textContent !== want) c.tx.textContent = want;
      }
      if (c.sweep) {
        const ease = checklistSweep(ct, V);
        const w = Math.min((c.tx.getComputedTextLength
          ? c.tx.getComputedTextLength() : V.SWEEP_W_FALLBACK) + V.SWEEP_PAD,
          (c.room || V.SWEEP_W_FALLBACK) + V.SWEEP_ROOM_PAD);
        c.sweep.setAttribute("width", (ease * w).toFixed(1));
        const band = c.el.querySelector("." + c.bandCls);
        if (band) band.setAttribute("width", (w).toFixed(1));
      }
    });
  });
}
