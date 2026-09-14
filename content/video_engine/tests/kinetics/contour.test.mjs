// P57 T12c / R26-70 (E76 s5: *"it's just math"*) - THE CONTOUR. Marching squares over a thresholded bitmap, which is
// how the engine gets a glyph's OUTLINE without parsing a font file. These tests pin the three bitmaps the header
// names - a square, an "O" (two rings, an outer and its hole), and two blobs - plus the SADDLE rule the header states
// (the foreground is 8-connected), the Douglas-Peucker simplify, and the purity the morph is built on: the same
// samples give the same rings, vertex for vertex.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CONTOUR, contourBitmap, contourSegments, contourWalk, contourRings, contourShape, pointInRing,
         simplifyRing } from "../../scripts/kinetics/contour.mjs";
import { polyArea } from "../../scripts/kinetics/arap.mjs";

/* a bitmap from a predicate - the only fixture these tests need */
const bmp = (w, h, ink) => {
  const data = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) data[y * w + x] = ink(x, y) ? 1 : 0;
  return { w, h, data };
};
const SQUARE = bmp(5, 5, (x, y) => x >= 1 && x <= 3 && y >= 1 && y <= 3);
/* an "O": a one-pixel-thick ring of ink round a 3x3 hole */
const RING_O = bmp(7, 7, (x, y) => (x >= 1 && x <= 5 && y >= 1 && y <= 5) && !(x >= 2 && x <= 4 && y >= 2 && y <= 4));
const TWO_BLOBS = bmp(9, 5, (x, y) => ((x >= 1 && x <= 2) || (x >= 6 && x <= 7)) && y >= 1 && y <= 3);

test("the dials are frozen and the level is the half-way one", () => {
  assert.equal(Object.isFrozen(CONTOUR), true);
  assert.equal(CONTOUR.LEVEL, 0.5, "a binary bitmap's contour is its 0.5 level");
});

// ---------------------------------------------------------------- the bitmap
test("the bitmap is the ALPHA channel thresholded - canvas's own stride and offset", () => {
  const rgba = new Uint8ClampedArray(4 * 4);   // 4 samples: alpha 0, 120, 128, 255
  [0, 120, 128, 255].forEach((a, i) => { rgba[i * 4 + 3] = a; });
  const b = contourBitmap(rgba, 4, 1);
  assert.deepEqual([...b.data], [0, 0, 1, 1], "128 of 255 is at the 0.5 level and is ink; 120 is paper");
  assert.deepEqual([b.w, b.h], [4, 1]);
  const low = contourBitmap(rgba, 4, 1, 0.4);
  assert.deepEqual([...low.data], [0, 1, 1, 1], "the threshold is a dial the caller states");
});

// ---------------------------------------------------------------- a square
test("A SQUARE comes back as ONE ring, closed, wound positive, with its corners cut", () => {
  const rings = contourRings(SQUARE);
  assert.equal(rings.length, 1, "one block of ink is one ring");
  assert.equal(rings[0].hole, false);
  assert.equal(rings[0].parent, -1);
  assert.ok(polyArea(rings[0].pts) > 0, "every ring is handed back wound positive");
  /* the 3x3 block spans (0.5, 0.5) - (3.5, 3.5) in SAMPLE space: area 9, less the four corner cells, each of which
     marching squares cuts diagonally between two edge midpoints (half of a half-cell): 9 - 4 * 0.125 = 8.5 */
  assert.equal(rings[0].area, 8.5);
  const xs = rings[0].pts.map((p) => p[0]), ys = rings[0].pts.map((p) => p[1]);
  assert.deepEqual([Math.min(...xs), Math.max(...xs)], [0.5, 3.5], "sample (i, j) is the CENTRE of pixel (i, j)");
  assert.deepEqual([Math.min(...ys), Math.max(...ys)], [0.5, 3.5]);
  assert.equal(new Set(rings[0].pts.map((p) => p.join(","))).size, rings[0].pts.length,
               "a closed ring is not handed its own start vertex twice");
});

// ---------------------------------------------------------------- an "O"
test("AN O comes back as TWO rings - the outer, and the HOLE inside it that knows its parent", () => {
  const rings = contourRings(RING_O);
  assert.equal(rings.length, 2);
  assert.equal(rings[0].hole, false, "the larger ring is the outline");
  assert.equal(rings[1].hole, true, "the one inside it is the counter");
  assert.equal(rings[1].parent, 0, "and it names the ring it is a hole in");
  assert.ok(rings[0].area > rings[1].area, "largest first: a parent is found before its children");
  assert.equal(rings[0].area, 24.5);   // the 5x5 block, corners cut
  assert.equal(rings[1].area, 8.5);    // the 3x3 hole, corners cut
  assert.ok(polyArea(rings[1].pts) > 0, "a hole is wound POSITIVE too - the topology is in `hole`, not the winding");
  assert.equal(pointInRing(rings[1].c, rings[0].pts), true, "the hole's centroid is inside the outline");
  assert.equal(pointInRing([0, 0], rings[0].pts), false);
});

test("A COUNTER ISLAND inside a hole is ink again - the parity rule, not the first ring that contains it", () => {
  /* a hollow square with a solid pip in the middle of its hole: outer, hole, island */
  const b = bmp(11, 11, (x, y) => {
    const outer = x >= 1 && x <= 9 && y >= 1 && y <= 9, hole = x >= 3 && x <= 7 && y >= 3 && y <= 7;
    const pip = x >= 5 && x <= 5 && y >= 5 && y <= 5;
    return (outer && !hole) || pip;
  });
  const rings = contourRings(b);
  assert.equal(rings.length, 3);
  assert.deepEqual(rings.map((r) => r.hole), [false, true, false], "inside an odd number of rings is a hole, inside two is ink");
  assert.equal(rings[2].parent, 1, "and the island's parent is the HOLE it sits in, the smallest ring that contains it");
});

// ---------------------------------------------------------------- two blobs
test("TWO BLOBS come back as TWO rings, neither a hole, each its own ink", () => {
  const rings = contourRings(TWO_BLOBS);
  assert.equal(rings.length, 2);
  assert.deepEqual(rings.map((r) => r.hole), [false, false]);
  assert.deepEqual(rings.map((r) => r.parent), [-1, -1]);
  assert.deepEqual(rings.map((r) => r.area), [5.5, 5.5], "the two 2x3 blocks are the same ink");
  const cx = rings.map((r) => r.c[0]).sort((a, z) => a - z);
  assert.ok(cx[1] - cx[0] > 3, "and they are apart: two glyphs, never one");
  assert.equal(pointInRing(rings[0].c, rings[1].pts), false, "neither is inside the other");
});

// ---------------------------------------------------------------- the saddle
test("THE AMBIGUOUS SADDLE is resolved so the FOREGROUND is 8-connected - the rule the header states", () => {
  /* two ink pixels touching only at a corner: case 5 / case 10. Under the foreground-connected rule the cell's two
     segments cut the two PAPER corners off and the ink runs through the middle, so this is ONE ring, not two. */
  const diag = bmp(4, 4, (x, y) => (x === 1 && y === 1) || (x === 2 && y === 2));
  assert.equal(contourRings(diag).length, 1, "the ink is joined through the saddle");
  const anti = bmp(4, 4, (x, y) => (x === 2 && y === 1) || (x === 1 && y === 2));
  assert.equal(contourRings(anti).length, 1, "and the other diagonal is the other saddle case, ruled the same way");
  /* the two paper corners, by the same rule, are SEPARATE fields - that is what 4-connected background means */
  const seg = contourSegments(diag);
  assert.equal(seg.segs.length % 2, 0, "every segment end lands on a midpoint another cell also puts one on");
  for (const ring of contourWalk(diag)) assert.ok(ring.length >= 3, "every walked chain closes");
});

// ---------------------------------------------------------------- the simplify
test("DOUGLAS-PEUCKER takes the raster's staircase off and leaves the ring's own corners", () => {
  const rings = contourRings(bmp(24, 24, (x, y) => x >= 2 && x <= 21 && y >= 2 && y <= 21));
  const raw = rings[0].pts;
  const cut = simplifyRing(raw, 0.4);
  assert.ok(cut.length < raw.length / 4, `the ring loses the staircase (${raw.length} -> ${cut.length})`);
  assert.equal(cut.length, 8, "and keeps the eight vertices a marching-squares square HAS - four corners, each bevelled");
  assert.equal(Math.abs(polyArea(cut)), rings[0].area, "the shape is the same shape, to the digit");
  assert.deepEqual(simplifyRing(raw, 0), raw, "a tolerance of nothing simplifies nothing");
  assert.deepEqual(simplifyRing([[0, 0], [1, 0], [0, 1]], 5), [[0, 0], [1, 0], [0, 1]],
                   "a triangle cannot be simplified below three vertices");
});

test("contourShape carries the rings out of sample space by ONE affine step, after the simplify", () => {
  const shape = contourShape(RING_O, { tol: 0.3, map: (p) => [p[0] * 2 + 100, p[1] * 2 - 50] });
  assert.equal(shape.length, 2);
  assert.deepEqual(shape.map((r) => r.hole), [false, true]);
  assert.ok(shape[0].pts.every((p) => p[0] >= 100 && p[1] >= -50), "every vertex is in the caller's units");
  const plain = contourShape(RING_O, { tol: 0.3 });
  assert.deepEqual(shape[0].pts, plain[0].pts.map((p) => [p[0] * 2 + 100, p[1] * 2 - 50]),
                   "the map is applied to the SIMPLIFIED ring: the tolerance is in the bitmap's own units");
});

// ---------------------------------------------------------------- the purity the morph is built on
test("THE SAME BITMAP GIVES THE SAME RINGS, vertex for vertex - a cold seek re-rasterises and lands where a play did", () => {
  for (const b of [SQUARE, RING_O, TWO_BLOBS]) {
    assert.deepEqual(contourRings(b), contourRings(b));
    assert.deepEqual(contourShape(b, { tol: 0.4 }), contourShape(b, { tol: 0.4 }));
  }
  assert.deepEqual(contourRings(bmp(5, 5, () => false)), [], "a bitmap with no ink has no rings");
  assert.deepEqual(contourRings(bmp(3, 3, () => true)).length, 1, "and one that is all ink has one, at its edge");
});
