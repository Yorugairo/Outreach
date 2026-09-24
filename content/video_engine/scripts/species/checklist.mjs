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
     profile- P69 T28b / R26-300: a spec that names `profile` takes that profile's dial set (CHECKLIST_PROFILES) for
              the build, the painter and the chart's header, on the dock's own canvas; a spec that names none takes
              CHECKLIST itself - the default card, and every pixel of the `test-card` golden, cannot move.
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

/* THE PHONE PROFILE (P69 T28b / R26-300; row 20's frame read). The default card writes 19 px cells on the dock's
   1056 x 480 canvas: at the right 0.60 of the stage (1152 px, the canvas at ~1.09x) that is ~20 stage px, a third of
   the long-form phone floor (E99 s90: 12 px on a 390 px phone = 59.08 stage px, ledger_page.CARD_PHONE_FLOOR), and the
   three rows used the canvas' upper half. Under `profile: "phone"` the TYPE, the header, the title, the row PITCH and
   the highlighter BAND scale together on the SAME canvas (the card's aspect is unchanged): cells at CELL_PX, the head
   at HEAD_PX, the title at TITLE_PX (all at or over the floor as displayed at 0.60 of the stage), row 1 at PT + 130
   and a 90 pitch, so three rows fill it to its foot (the last baseline at 406 of 480). The sizes are inline styles
   written by this module (an inline style outranks the template's .chartbox class fonts), so the band that is cut to
   the type and the type are stated in one place. A phone card is a QUESTION AND ITS TWO ANSWERS (Ask / Steel / Paper;
   the chips already said where to look): both answers take the marker (HL_FROM_COL 1), it has no sub line (the
   title carries it, as the T10c card profile), and it holds three rows at the floor - the compiler refuses the rest
   by name (build_scene_timeline_f.checklist_problems). */
export const CHECKLIST_PROFILES = Object.freeze({
  phone: Object.freeze({
    ...CHECKLIST,
    COLORS: Object.freeze(["#f4f6f8", "#3bc9b0", "#ff8a8c"]),   /* the default card's question, steel and paper - no detail column */
    TYPE: Object.freeze({ TITLE_PX: 62, HEAD_PX: 57, CELL_PX: 58, SRC_PX: 24 }),   /* the canvas font sizes (CSS px in the viewBox): the
                           dock's chartbox is 1110 px wide inside a 0.60 dock (1152 px), 1.051x the canvas, so 57 is 59.9 displayed */
    CANVAS: Object.freeze({ PL: 28, PR: 28, PT: 96, TITLE_X: 28, TITLE_Y: 66, SRC_X: 28, SRC_DY: 14 }),   /* the chart's frame on the canvas */
    HEAD_DY: 50,           /* the header's baseline below the plot top (146: clear of the title's descenders) */
    ROW0_DY: 130,          /* row 1's baseline below the plot top (226) ... */
    ROW_PITCH: 90,         /* ... and the pitch: 226 / 316 / 406 on a 480 canvas */
    HL_FROM_COL: 1,        /* both answers take the marker */
    BAND_INSET: 12,        /* the band, cut to the 58 px cell: this far left of its column ... */
    BAND_RISE: 52,         /* ... this far above the baseline (the cap height and a little air) ... */
    BAND_H: 70,            /* ... this tall (to the descenders; 20 px of ground between two rows' bands) ... */
    BAND_W0: 24,           /* ... at this initial width ... */
    BAND_RX: 9,            /* ... with this corner radius */
    RULE_DY: 26,           /* the row rule, under the descenders */
    FIT_MARGIN: 28,        /* the usable span = CW - PL - this (the columns run to the canvas' right margin) */
    FIT_PAD: 36,           /* a column's air at this type */
    FIT_CHAR_W: 30,        /* the width per character when the DOM cannot measure */
    FIT_X0: 28,            /* the first column's x = PL */
    FIT_KEEP_Q: true,      /* the question column keeps its natural width - it TYPES, so it is never squeezed (a textLength
                              would stretch its first letters across the column); only the answers give way */
    FIT_ROOM_SLACK: 14,    /* a cell's room = its allotment - FIT_PAD + this */
    SWEEP_PAD: 30,         /* the sweep runs this past the text ... */
    SWEEP_ROOM_PAD: 20,    /* ... capped at the cell's room plus this */
  }),
});

/* the dial set a spec draws with: its named profile, or CHECKLIST itself (the default card, the same object) */
export const checklistDials = (spec, V = CHECKLIST) => {
  const name = spec ? spec.profile : null;
  if (name === undefined || name === null) return V;
  if (!Object.prototype.hasOwnProperty.call(CHECKLIST_PROFILES, name))
    throw new Error(`checklist profile '${name}' is not one of ${Object.keys(CHECKLIST_PROFILES).join(", ")}`);
  return CHECKLIST_PROFILES[name];
};

/* the chart's profile when it is a checklist that names one, else null - the engine's chart build reads its frame */
export const checklistProfile = (C) => (C && C.checklist && C.checklist.profile != null) ? checklistDials(C.checklist) : null;

/* a text element's size under a profile (an inline style), and nothing at all on the default card */
const checklistType = (V, key) => V.TYPE ? { style: `font-size:${V.TYPE[key]}px` } : {};

/* THE PROFILE'S HEADER, for the engine's chart build: the title at its size and place, no sub (the title carries it),
   the source at the foot. Returns the [element, max width] pairs the engine clamps at its first tick. */
export function checklistHeader(C, mk, CW, CH, V) {
  const cv = V.CANVAS;
  return [
    [mk("text", { class: "ct", x: cv.TITLE_X, y: cv.TITLE_Y, ...checklistType(V, "TITLE_PX") }, C.title), CW - 56],
    [mk("text", { class: "csr", x: cv.SRC_X, y: CH - cv.SRC_DY, ...checklistType(V, "SRC_PX") }, C.src), CW - 56],
  ];
}

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

/* THE COLUMN FIT from the natural widths: allotments, the squeeze, the spread slack and each column's x (under
   FIT_KEEP_Q the squeeze falls on the answer columns alone) */
export const checklistColumns = (natW, usable, V = CHECKLIST) => {
  const NC = natW.length;
  const alloc = natW.map((w) => w + V.FIT_PAD);
  const total = alloc.reduce((a, b) => a + b, 0);
  const keep = V.FIT_KEEP_Q ? alloc[0] : 0;   /* P69 T28b: a profile may hold the question column at its natural width */
  const scale2 = total > usable ? (usable - keep) / (total - keep) : 1;
  const extra = total < usable ? (usable - total) / NC : 0;
  const xs = []; let acc = V.FIT_X0;
  for (let ci = 0; ci < NC; ci++) {
    xs.push(acc); acc += (keep && ci === 0 ? alloc[ci] : alloc[ci] * scale2) + extra;
  }
  return { alloc, scale2, extra, xs };
};

/* THE BUILD, inside the chart build: ctx = { mk, slot, PL, PT, CW, PR, kin } from the engine's chart scope (under a
   profile, PL / PR / PT are the profile's CANVAS). Returns { rowEls, chkFit } for the chart state; chkFit.V is the
   dial set the painter reads. */
export function buildChecklist(spec, ctx, V = checklistDials(spec)) {
  const { mk, slot, PL, PT, CW, PR, kin } = ctx;
  const headEls = spec.head.map((h) =>
    mk("text", { class: "csr", x: PL, y: PT + V.HEAD_DY, ...checklistType(V, "HEAD_PX") }, h));
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
         fill: colr[ci], ...checklistType(V, "CELL_PX") }, ci === 0 ? "" : cell, g2);
      cells.push({ el: g2, tx, txt: cell, ci, sweep, band, y,
                   bandCls: "hlband" + slot + i + ci });
    });
    mk("line", { x1: PL, x2: CW - PR, y1: y + V.RULE_DY, y2: y + V.RULE_DY,
       stroke: V.RULE_COLOR, "stroke-width": V.RULE_W });
    rowEls.push({ d: r.delay || i * V.ROW_DELAY_S, cells, y });
  });
  return { rowEls, chkFit: { headEls, done: false, usable: CW - PL - V.FIT_MARGIN, V } };
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

/* THE PAINTER, inside drawChart on the dock's clock tRel: the one-time fit, then every row's cells, on the dial set
   the build used. */
export function paintChecklist(st, tRel, d, V = (st.chkFit && st.chkFit.V) || CHECKLIST) {
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
