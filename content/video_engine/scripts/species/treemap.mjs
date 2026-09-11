/* species/treemap.mjs - THE CENSUS PAGE and its X MARKS (P50 T6; E53 s1's second amendment, the
   census exception, ruled 2026-09-10; Bravos shots 89-91). SOURCE OF TRUTH, inlined into the
   scene-evidence player by sync_kinetics.py between KINETICS:BEGIN treemap and KINETICS:END, AFTER
   ease. Its region sits with the kinetics laws for span.mjs's reason: the page's builder and the
   page's PERFORM layer both call it, and both are written far above the species block.

   WHERE THE LAYOUT IS. Not here. The squarified rectangles (Bruls, Huizing & van Wijk 2000, tuned
   toward 3:2 rather than the paper's square - Heer & Bostock 2010) are computed by ledger_page.py at
   BUILD time, inside page_boxes' own plot, and ride the spec as fractions of that plot. This module
   maps a cell's fractions into the rect it is drawn in and owns the CLOCK. That split is the point:
   a layout computed at paint time is a re-layout waiting to happen, and E58 (with Sondag 2018) says
   the shrink afterwards is ONE affine transform - cells never hop. `treemapRect` is linear in the
   plot rect, which is what makes the park free: scaling the rect scales every cell exactly.

   WHEN: the sentence takes a CENSUS - "China sells to everyone", "three partners, 41 % of exports".
   Never a size comparison between two cells: that is a bar's job, and `ledger_page.py` refuses the
   file whose own words make one.

   THE LAW, a pure function of the build fraction c and of t:
     cells  - they land in LAYOUT order (largest first), each over CELL_IN of the clock, staggered
              across STAGGER of it - the bars' law, on a mosaic; the label writes once its own cell
              is nearly in, and only on the cells the compiler said had room (the research's floors).
     cross  - the named cells take a two-stroke X over CROSS_S (the chip's cross, the same dial: one
              cross law on the page) and dim to DIM while it is struck. The X is the mark; the DIM is
              what keeps a crossed cell part of the census instead of deleting it.
     share  - and the crossed share is WRITTEN by the hand over WRITE of the word - E53 s1's second
              amendment (b), which is why the species carries both halves and the compiler refuses
              one without the other.
   The dials are ours to tune (42 s42.5), not findings. */

export const TREEMAP = Object.freeze({
  CELL_IN: 0.30,      /* one cell's own landing, as a share of the build clock */
  STAGGER: 0.70,      /* ... and the share of the clock spent handing from the first cell to the last */
  LABEL_AT: 0.55,     /* a cell's label writes from this much of its own landing: the tile first, its name after */
  RISE: 0.35,         /* the cell grows from this share of its own size as it lands (the bar's scale, in two dimensions) */
  CROSS_S: 0.5,       /* the X's two strokes together - the chip's own dial (species/chip.mjs CROSS_S), deliberately */
  CROSS_INSET: 0.12,  /* the X's inset from the cell's corners, as a share of the cell's SHORTER side */
  DIM: 0.55,          /* what a crossed cell dims to: struck, still legible, still counted (the census does not delete) */
  WRITE: 0.45,        /* the share of the word the hand takes to write the crossed share, once the X's are struck */
  WRITE_AT: 0.35,     /* ... starting here, so the number arrives while the last X is still being drawn */
});

const tm01 = (v) => Math.min(1, Math.max(0, v));

/* A CELL'S RECT inside the plot it is drawn in. Linear in the plot: scale or translate the plot and
   every cell follows exactly, which is the park (E58: one affine transform, never a re-layout). */
export const treemapRect = (cell, plot) => ({
  x: plot.x + (+cell.fx || 0) * plot.w,
  y: plot.y + (+cell.fy || 0) * plot.h,
  w: (+cell.fw || 0) * plot.w,
  h: (+cell.fh || 0) * plot.h,
});

/* the landing of cell i of n at build fraction c: layout order, the bars' stagger */
export const treemapCellK = (c, i, n) => {
  const span = n > 1 ? TREEMAP.STAGGER / (n - 1) : 0;
  return tm01((c - (i | 0) * span) / TREEMAP.CELL_IN);
};

/* the cell's own scale as it lands, about its centre, and its label's opacity */
export const treemapCellScale = (k) => TREEMAP.RISE + (1 - TREEMAP.RISE) * k;
export const treemapLabelK = (k) => tm01((k - TREEMAP.LABEL_AT) / (1 - TREEMAP.LABEL_AT));

/* WHICH CELLS a cross names, by label, in the page's own order. A name the page does not carry
   resolves to nothing here and is refused at build time by the compiler - the player never guesses. */
export const treemapNamed = (cells, names) => {
  const want = new Set((names || []).map(String));
  return (cells || []).map((c, i) => (want.has(String(c.label)) ? i : -1)).filter((i) => i >= 0);
};

/* THE CROSS at t: 0 until the species' word, 1 CROSS_S later. */
export const treemapCrossF = (sp, t) => tm01((t - +sp.at) / TREEMAP.CROSS_S);

/* the two strokes of the X from the cross's fraction: the first over its first half, the second over
   the second - the chip's law, so one X on the page is drawn like every other */
export const treemapStrokes = (cross) => [tm01(cross * 2), tm01(cross * 2 - 1)];

/* the two diagonals of a cell's X, inset from its corners by a share of its shorter side */
export const treemapCrossLines = (r, inset = TREEMAP.CROSS_INSET) => {
  const d = Math.min(r.w, r.h) * inset;
  const x0 = r.x + d, x1 = r.x + r.w - d, y0 = r.y + d, y1 = r.y + r.h - d;
  return [{ x1: x0, y1: y0, x2: x1, y2: y1 }, { x1: x1, y1: y0, x2: x0, y2: y1 }];
};

/* a crossed cell dims while it is struck, and holds there: it is still one of the parts */
export const treemapDim = (cross) => 1 - (1 - TREEMAP.DIM) * tm01(cross);

/* the hand writing the crossed share, and one glyph of it (the span's and the figure's own law: the
   share is 1 / (n + 0.6) so the last glyph lands exactly as the write ends) */
export const treemapWrite = (sp, t) => {
  const dur = Math.max(0.001, +sp.dur || 1);
  return tm01((t - +sp.at - TREEMAP.WRITE_AT) / (dur * TREEMAP.WRITE));
};
export const treemapGlyph = (write, j, n) => {
  const per = 1 / (Math.max(1, n | 0) + 0.6);
  return tm01((write - j * per) / (per * 1.6));
};
