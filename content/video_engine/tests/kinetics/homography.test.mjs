// P50 T7 - THE PLANAR PROJECTION (the ART-embed world). The unit square to an axis-aligned rectangle is AFFINE
// (no perspective terms at all); a known keystone returns its own four corners to 1e-9; the identity quad's
// matrix3d is the identity matrix; and the card's box is letterboxed inside the quad and lands on it.
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  H_IDENTITY, quadPoints, hFromUnitSquare, hApply, hMul, hTranslate, hAffine, hAbout,
  cssMatrix3d, quadBounds, embedBox, embedMatrix, embedRegion,
} from "../../scripts/kinetics/homography.mjs";

const UNIT = [[0, 0], [1, 0], [1, 1], [0, 1]];
// the POSTER measured off the plate still (art-embed-study-poster.png, 768 x 1376): the frame's inner corners,
// in stage px at 1080 x 1920 - vertical sides, the top edge rising to the right, the right side the taller one
const POSTER = [[397.9, 372.6], [897.2, 299.5], [897.2, 1199.4], [397.9, 1172.4]];
const near = (a, b, eps = 1e-9) => Math.abs(a - b) < eps;

test("the unit square to an AXIS-ALIGNED RECT is affine: no perspective terms, and the map is x -> a x + c", () => {
  const rect = [[100, 50], [500, 50], [500, 350], [100, 350]];
  const h = hFromUnitSquare(rect);
  assert.equal(h[6], 0, "h20");
  assert.equal(h[7], 0, "h21");
  assert.deepEqual(h.slice(0, 6), [400, 0, 100, 0, 300, 50]);
  assert.deepEqual(hApply(h, 0.5, 0.5), [300, 200], "the centre of the square is the centre of the rect");
  // a PARALLELOGRAM is affine too - the projective terms exist only when the quad's opposite edges converge
  const par = hFromUnitSquare([[0, 0], [100, -20], [140, 80], [40, 100]]);
  assert.equal(par[6], 0);
  assert.equal(par[7], 0);
});

test("a known KEYSTONE gives its four corners back within 1e-9, and the map is projective", () => {
  const keystone = [[100, 100], [500, 140], [560, 400], [60, 460]];   // a plate surface angled away at the top
  const h = hFromUnitSquare(keystone);
  assert.ok(h[6] !== 0 || h[7] !== 0, "converging edges must produce perspective terms");
  for (const [i, [u, v]] of [[0, 0], [1, 0], [1, 1], [0, 1]].entries()) {
    const p = hApply(h, u, v);
    assert.ok(near(p[0], keystone[i][0]) && near(p[1], keystone[i][1]),
      `corner ${i}: ${p} != ${keystone[i]}`);
  }
  // the POSTER read off the plate: the same law on the real surface, and its centre lands inside it
  const hp = hFromUnitSquare(POSTER);
  for (const [i, [u, v]] of [[0, 0], [1, 0], [1, 1], [0, 1]].entries()) {
    const p = hApply(hp, u, v);
    assert.ok(near(p[0], POSTER[i][0]) && near(p[1], POSTER[i][1]), `poster corner ${i}`);
  }
  const c = hApply(hp, 0.5, 0.5);
  assert.ok(c[0] > 397.9 && c[0] < 897.2 && c[1] > 372.6 && c[1] < 1199.4, `the centre is on the surface: ${c}`);
});

test("the projection is a straight-line map: a straight edge stays straight under perspective", () => {
  const h = hFromUnitSquare([[100, 100], [500, 140], [560, 400], [60, 460]]);
  const a = hApply(h, 0, 0.5), b = hApply(h, 1, 0.5), m = hApply(h, 0.5, 0.5);
  // the midpoint of the unit segment is NOT the midpoint of the image (that is what perspective means)...
  assert.ok(Math.abs(m[0] - (a[0] + b[0]) / 2) > 1e-9 || Math.abs(m[1] - (a[1] + b[1]) / 2) > 1e-9);
  // ... but it IS on the line through the two ends
  const cross = (b[0] - a[0]) * (m[1] - a[1]) - (b[1] - a[1]) * (m[0] - a[0]);
  assert.ok(Math.abs(cross) < 1e-6, `collinear: cross ${cross}`);
});

test("matrix3d of the IDENTITY quad is the identity matrix", () => {
  const h = hFromUnitSquare([[0, 0], [1, 0], [1, 1], [0, 1]]);
  assert.deepEqual(h, [...H_IDENTITY]);
  assert.equal(cssMatrix3d(h), "matrix3d(" + [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    .map((v) => v.toFixed(9)).join(", ") + ")");
  assert.equal(cssMatrix3d(null), "none");
  // the perspective terms land in the fourth argument of each of the first two columns (m14, m24)
  const k = hFromUnitSquare([[100, 100], [500, 140], [560, 400], [60, 460]]);
  const m = cssMatrix3d(k).slice("matrix3d(".length, -1).split(", ").map(Number);
  assert.ok(near(m[3], k[6], 1e-9) && near(m[7], k[7], 1e-9), "m14 = h20, m24 = h21");
  assert.deepEqual(m.slice(8, 12), [0, 0, 1, 0], "z is left alone");
  assert.ok(near(m[12], k[2], 1e-6) && near(m[13], k[5], 1e-6), "the translation is the fourth column");
});

test("composition keeps h22 = 1, and a translate then a projection is the projection moved", () => {
  const h = hFromUnitSquare([[100, 100], [500, 140], [560, 400], [60, 460]]);
  const moved = hMul(hTranslate(20, -7), h);
  for (const [u, v] of UNIT) {
    const a = hApply(h, u, v), b = hApply(moved, u, v);
    assert.ok(near(b[0], a[0] + 20) && near(b[1], a[1] - 7), `${a} -> ${b}`);
  }
  assert.deepEqual(hMul(H_IDENTITY, h).map((v) => +v.toFixed(12)), h.map((v) => +v.toFixed(12)));
  // hAffine is the CSS matrix(a b c d e f) order, and hAbout applies it about a point
  const scale2 = hAffine(2, 0, 0, 2, 0, 0);
  assert.deepEqual(hApply(scale2, 3, 4), [6, 8]);
  assert.deepEqual(hApply(hAbout(scale2, 10, 10), 10, 10), [10, 10], "the pivot does not move");
  assert.deepEqual(hApply(hAbout(scale2, 10, 10), 11, 12), [12, 14]);
});

test("a degenerate quad has no map, and a malformed one is refused rather than guessed", () => {
  assert.equal(hFromUnitSquare([[0, 0], [1, 1], [2, 2], [3, 3]]), null, "four collinear corners");
  assert.equal(hFromUnitSquare([[0, 0], [1, 0], [1, 1]]), null, "three corners");
  assert.equal(hFromUnitSquare([[0, 0], [1, 0], [1, 1], ["x", 1]]), null);
  assert.equal(quadPoints(null), null);
  assert.deepEqual(quadPoints(UNIT), UNIT.map(([x, y]) => [x, y]));
});

test("the card's BOX is its own aspect, letterboxed in the quad's bounds and centred there", () => {
  const b = quadBounds(POSTER);
  assert.ok(near(b.x, 397.9) && near(b.y, 299.5) && near(b.w, 499.3, 1e-9) && near(b.h, 899.9, 1e-9));
  const wide = embedBox(POSTER, 0.5);                 // a card half as tall as it is wide: the width binds
  assert.ok(near(wide.w, b.w) && near(wide.h, b.w * 0.5));
  assert.ok(near(wide.x, b.x) && near(wide.y + wide.h / 2, b.y + b.h / 2), "centred in the bounds");
  const tall = embedBox(POSTER, 4);                   // a tall card: the height binds
  assert.ok(near(tall.h, b.h) && near(tall.w, b.h / 4));
  assert.ok(near(tall.x + tall.w / 2, b.x + b.w / 2) && near(tall.y, b.y));
  assert.equal(embedBox([[0, 0], [0, 0], [0, 0], [0, 0]], 1), null, "a quad with no area has no box");
});

test("the ELEMENT matrix carries the card's own corners onto the surface, in its own coordinates", () => {
  const box = embedBox(POSTER, 1.2), m = embedMatrix(POSTER, box);
  const H = hFromUnitSquare(POSTER), b = quadBounds(POSTER);
  for (const [lx, ly] of [[0, 0], [box.w, 0], [box.w, box.h], [0, box.h], [box.w / 3, box.h / 7]]) {
    const got = hApply(m, lx, ly);                    // the matrix is written as an OFFSET from the box origin
    const want = hApply(H, (box.x + lx - b.x) / b.w, (box.y + ly - b.y) / b.h);
    assert.ok(near(got[0] + box.x, want[0], 1e-8) && near(got[1] + box.y, want[1], 1e-8), `${got} vs ${want}`);
  }
  // a card whose aspect matches the quad's bounds exactly fills them, so its corners ARE the quad's corners
  const full = embedBox(POSTER, b.h / b.w), mf = embedMatrix(POSTER, full);
  const corners = [[0, 0], [full.w, 0], [full.w, full.h], [0, full.h]];
  corners.forEach(([lx, ly], i) => {
    const p = hApply(mf, lx, ly);
    assert.ok(near(p[0] + full.x, POSTER[i][0], 1e-8) && near(p[1] + full.y, POSTER[i][1], 1e-8), `corner ${i}`);
  });
  assert.equal(embedMatrix(POSTER, { x: 0, y: 0, w: 0, h: 10 }), null);
});

test("a region INSIDE the card (the quoted phrase) comes back as four projected corners and their box", () => {
  const box = embedBox(POSTER, 1.2), m = embedMatrix(POSTER, box);
  const phrase = { x: box.x + box.w * 0.1, y: box.y + box.h * 0.6, w: box.w * 0.8, h: box.h * 0.12 };
  const r = embedRegion(m, box, phrase);
  assert.equal(r.quad.length, 4);
  // the surface's top edge RISES to the right, so the phrase's own top edge does too - it is in the projected space
  assert.ok(r.quad[1][1] < r.quad[0][1], "the right end of the phrase sits higher than the left");
  assert.ok(r.quad[3][1] > r.quad[0][1] && r.quad[2][1] > r.quad[1][1]);
  const xs = r.quad.map((p) => p[0]), ys = r.quad.map((p) => p[1]);
  assert.ok(near(r.x, Math.min(...xs)) && near(r.y, Math.min(...ys)));
  assert.ok(near(r.w, Math.max(...xs) - r.x) && near(r.h, Math.max(...ys) - r.y));
  assert.ok(r.h > phrase.h, "the bounding box of a slanted band is taller than the band");
  assert.equal(embedRegion(null, box, phrase), null);
});

test("THE SURFACE IS THE CARD: the quad's whole bounding rectangle lands corner on corner", () => {
  // what embedPlace passes since the second watch (the operator, 2026-09-12: "isn't the whole point of the TV
  // to use it as the entire surface?"): the card is laid out at the WHOLE bounding rectangle of the quad, so
  // the projection carries its four corners onto the surface's four corners and the card fills it. The card's
  // own aspect never enters - the box carries the SURFACE'S aspect and the card reflows into it.
  const b = quadBounds(POSTER), m = embedMatrix(POSTER, b);
  [[0, 0], [b.w, 0], [b.w, b.h], [0, b.h]].forEach(([lx, ly], i) => {
    const p = hApply(m, lx, ly);
    assert.ok(near(p[0] + b.x, POSTER[i][0], 1e-8) && near(p[1] + b.y, POSTER[i][1], 1e-8), `corner ${i}`);
  });
  const mid = hApply(m, b.w / 2, b.h / 2);
  assert.ok(mid[0] + b.x > b.x && mid[0] + b.x < b.x + b.w, "the card's middle stays on the surface");
  assert.ok(mid[1] + b.y > b.y && mid[1] + b.y < b.y + b.h);
});
