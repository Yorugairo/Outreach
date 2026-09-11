// P50 T6 - THE CENSUS PAGE and its X MARKS (E53 s1's second amendment; Bravos shots 89-91). The
// LAYOUT is python's (ledger_page.squarify, at build time, in page_boxes' plot); this module maps a
// cell into the rect it is drawn in and owns the clock. These tests pin that split - above all that
// the mapping is AFFINE in the plot, which is what makes the shrink afterwards a park and not a
// re-layout (E58; Sondag 2018) - and the two halves of the census exception: the X and the share.
import { test } from "node:test";
import assert from "node:assert/strict";
import { TREEMAP, treemapRect, treemapCellK, treemapCellScale, treemapLabelK, treemapNamed,
         treemapCrossF, treemapStrokes, treemapCrossLines, treemapDim, treemapWrite, treemapGlyph } from "../../scripts/species/treemap.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const CELLS = [
  { label: "United States", fx: 0, fy: 0, fw: 0.4, fh: 0.5 },
  { label: "Hong Kong", fx: 0, fy: 0.5, fw: 0.4, fh: 0.5 },
  { label: "Japan", fx: 0.4, fy: 0, fw: 0.6, fh: 0.3 },
];
const PLOT = { x: 100, y: 200, w: 600, h: 400 };
const sp = (o = {}) => Object.assign({ kind: "cross", at: 10, dur: 3, cells: ["Japan"], text: "3 partners, 41 % of exports" }, o);

test("the dials are the census page's, and a crossed cell is struck, not deleted", () => {
  assert.ok(TREEMAP.CELL_IN > 0 && TREEMAP.STAGGER > 0 && TREEMAP.STAGGER <= 1);
  assert.ok(TREEMAP.CROSS_S > 0 && TREEMAP.CROSS_INSET > 0 && TREEMAP.CROSS_INSET < 0.5);
  assert.ok(TREEMAP.DIM > 0.2 && TREEMAP.DIM < 1, "a crossed cell stays legible: the census counts it");
  assert.ok(TREEMAP.WRITE > 0 && TREEMAP.WRITE <= 1);
});

// ------------------------------------------------------------- the layout is not ours
test("a cell's rect is its fractions mapped into the plot - and the mapping is AFFINE in the plot", () => {
  const r = treemapRect(CELLS[0], PLOT);
  assert.deepEqual(r, { x: 100, y: 200, w: 240, h: 200 });
  // the park: the same plot scaled about its own origin scales every cell exactly, in place - no cell hops
  const s = 0.72;
  const parked = { x: PLOT.x, y: PLOT.y, w: PLOT.w * s, h: PLOT.h * s };
  for (const c of CELLS) {
    const a = treemapRect(c, PLOT), b = treemapRect(c, parked);
    assert.ok(near(b.w, a.w * s) && near(b.h, a.h * s), "a parked cell is the same cell, scaled");
    assert.ok(near(b.x - PLOT.x, (a.x - PLOT.x) * s) && near(b.y - PLOT.y, (a.y - PLOT.y) * s));
  }
  // ... and a translated plot translates them, nothing else
  const moved = treemapRect(CELLS[2], { ...PLOT, x: PLOT.x + 40, y: PLOT.y - 10 });
  const home = treemapRect(CELLS[2], PLOT);
  assert.ok(near(moved.x - home.x, 40) && near(moved.y - home.y, -10) && near(moved.w, home.w));
});

test("the cells land in LAYOUT order and every one is in by the end of the build", () => {
  const n = CELLS.length;
  assert.equal(treemapCellK(0, 0, n), 0);
  for (let i = 0; i < n; i++) assert.equal(treemapCellK(1, i, n), 1, "no cell is still arriving when the page is built");
  assert.ok(treemapCellK(0.3, 0, n) > treemapCellK(0.3, n - 1, n), "the biggest cell lands first (layout order)");
  assert.equal(treemapCellK(0.5, 0, 1), 1, "one cell has nothing to wait for");
  assert.ok(treemapCellScale(0) > 0 && treemapCellScale(0) < 1 && near(treemapCellScale(1), 1));
  assert.equal(treemapLabelK(TREEMAP.LABEL_AT), 0, "the tile first, its name after");
  assert.equal(treemapLabelK(1), 1);
});

// ------------------------------------------------------------------- the X marks
test("a cross names CELLS by label, and a name the page does not carry names nothing", () => {
  assert.deepEqual(treemapNamed(CELLS, ["Japan", "United States"]), [0, 2], "in the page's own order, never the sentence's");
  assert.deepEqual(treemapNamed(CELLS, ["Atlantis"]), [], "the player never guesses - the compiler refuses this at build time");
  assert.deepEqual(treemapNamed(CELLS, []), []);
  assert.deepEqual(treemapNamed([], ["Japan"]), []);
});

test("the X is two strokes, the first over the first half of the cross and the second over the second", () => {
  assert.equal(treemapCrossF(sp(), 9.9), 0, "nothing before the word");
  assert.equal(treemapCrossF(sp(), 10 + TREEMAP.CROSS_S), 1);
  assert.deepEqual(treemapStrokes(0), [0, 0]);
  assert.deepEqual(treemapStrokes(0.5), [1, 0], "the first stroke is complete exactly as the second begins");
  assert.deepEqual(treemapStrokes(1), [1, 1]);
  const [a, b] = treemapCrossLines({ x: 0, y: 0, w: 100, h: 50 });
  const d = 50 * TREEMAP.CROSS_INSET;
  assert.deepEqual(a, { x1: d, y1: d, x2: 100 - d, y2: 50 - d }, "inset by a share of the SHORTER side, so a wide cell's X is not a line");
  assert.deepEqual(b, { x1: 100 - d, y1: d, x2: d, y2: 50 - d });
});

test("a crossed cell dims and holds there", () => {
  assert.equal(treemapDim(0), 1);
  assert.equal(treemapDim(1), TREEMAP.DIM);
  assert.ok(treemapDim(0.5) > TREEMAP.DIM && treemapDim(0.5) < 1);
  assert.equal(treemapDim(2), TREEMAP.DIM, "it does not keep fading after the X is struck");
});

// ----------------------------------------------- the other half of the exception
test("the crossed SHARE is written by the hand, and the last glyph lands as the write ends", () => {
  const s = sp({ at: 10, dur: 4 });
  assert.equal(treemapWrite(s, 10), 0, "the number arrives while the X's are still being struck, never before them");
  assert.ok(treemapWrite(s, 10 + TREEMAP.WRITE_AT + 4 * TREEMAP.WRITE) >= 1);
  const n = 12;
  assert.equal(treemapGlyph(0, 0, n), 0);
  assert.equal(treemapGlyph(1, n - 1, n), 1, "the tail of the number is written by the time the word is over");
  assert.ok(treemapGlyph(0.5, 0, n) === 1 && treemapGlyph(0.5, n - 1, n) < 1, "glyph after glyph: a hand, not a ticker");
});
