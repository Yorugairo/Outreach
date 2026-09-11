// P50 T12 - the morph, METHOD A (43 s43.5): ring-normalise, resample, the rotational alignment, the vertex lerp and
// the cubic reconstruction. The acceptance case is a square becoming a circle: every intermediate ring is SIMPLE (no
// self-intersection) and its area moves monotonically from the one to the other.
import { test } from "node:test";
import assert from "node:assert/strict";
import { MORPH_A, ringNormalise, morphAPrepare, morphAAt, morphAPath, morphAMinDet, morphAArea } from "../../scripts/kinetics/morph_a.mjs";
import { polyArea, alignOffset, rotate, resample, stripMesh } from "../../scripts/kinetics/arap.mjs";

const square = (cx, cy, s) => [[cx - s / 2, cy - s / 2], [cx + s / 2, cy - s / 2], [cx + s / 2, cy + s / 2], [cx - s / 2, cy + s / 2]];
const circle = (cx, cy, r, n = 64, phase = 0) =>
  [...Array(n).keys()].map((i) => { const a = phase + (i / n) * Math.PI * 2; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });

/* segments that share an endpoint are neighbours on a ring; every other pair must not cross */
const segCross = (p1, p2, p3, p4) => {
  const d = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  const d1 = d(p3, p4, p1), d2 = d(p3, p4, p2), d3 = d(p1, p2, p3), d4 = d(p1, p2, p4);
  return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0));
};
const isSimple = (ring) => {
  const n = ring.length;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
    if (j === i || (j + 1) % n === i || (i + 1) % n === j) continue;
    if (segCross(ring[i], ring[(i + 1) % n], ring[j], ring[(j + 1) % n])) return false;
  }
  return true;
};

test("ring-normalise: one orientation, one start vertex, no duplicate knots", () => {
  const raw = [...square(500, 300, 200), [400, 400]];           // the closing duplicate of the last vertex
  const A = ringNormalise(raw);
  assert.ok(polyArea(A) > 0, "counter-clockwise by the shoelace, whichever way it came in");
  const B = ringNormalise(raw.slice().reverse());
  assert.deepEqual(A, B, "the same ring described backwards normalises to the same description");
  const C = ringNormalise(rotate(square(500, 300, 200), 2));
  assert.deepEqual(C, ringNormalise(square(500, 300, 200)), "and started at another vertex");
  assert.deepEqual(A[0], [400, 200], "the start vertex is the lowest, then leftmost");
  assert.equal(ringNormalise([[0, 0], [0, 0], [10, 0], [10, 10], [10, 10]]).length, 3, "duplicate knots are dropped");
});

test("the alignment picks the rotation that minimises the summed squared distance", () => {
  const A = square(500, 300, 200), B = circle(500, 300, 120, 4, 0.3);
  const prep = morphAPrepare(A, B, { n: 32 });
  const An = resample(ringNormalise(A), 32), Bn = resample(ringNormalise(B), 32);
  const cost = (k) => An.reduce((s, p, i) => { const q = Bn[(i + k) % 32]; return s + (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2; }, 0);
  const best = [...Array(32).keys()].reduce((b, k) => (cost(k) < cost(b) ? k : b), 0);
  assert.equal(prep.offset, best, "argmin_k sum ||v_A,i - v_B,(i+k)||^2");
  assert.equal(prep.offset, alignOffset(An, Bn));
  assert.deepEqual(prep.B, rotate(Bn, best), "B is carried onto A by that rotation, and nothing else");
});

test("the endpoints are the inputs exactly", () => {
  const A = resample(ringNormalise(square(500, 300, 200)), 48), B = resample(ringNormalise(circle(500, 300, 120)), 48);
  const prep = morphAPrepare(A, B, { resample: false });
  assert.deepEqual(morphAAt(prep, 0).outline, prep.A);
  assert.deepEqual(morphAAt(prep, 1).outline, prep.B);
  assert.deepEqual(morphAAt(prep, -0.5).outline, prep.A, "before the clock: the source, never an extrapolation");
  assert.deepEqual(morphAAt(prep, 2).outline, prep.B);
  const mid = morphAAt(prep, 0.5).outline;
  mid.forEach((p, i) => {
    assert.ok(Math.abs(p[0] - (prep.A[i][0] + prep.B[i][0]) / 2) < 1e-12, "a direct vertex lerp, per vertex");
    assert.ok(Math.abs(p[1] - (prep.A[i][1] + prep.B[i][1]) / 2) < 1e-12);
  });
});

test("a square becomes a circle: every intermediate ring is simple and its area is monotone between the two", () => {
  const prep = morphAPrepare(square(500, 300, 240), circle(500, 300, 120), { n: MORPH_A.N });
  const a0 = morphAArea(morphAAt(prep, 0).outline), a1 = morphAArea(morphAAt(prep, 1).outline);
  assert.ok(a0 > a1, "the square is the bigger of the two (240^2 against pi 120^2)");
  let prev = Infinity;
  for (let i = 0; i <= 24; i++) {
    const ring = morphAAt(prep, i / 24).outline, area = morphAArea(ring);
    assert.ok(isSimple(ring), `the ring at t = ${(i / 24).toFixed(2)} crosses itself`);
    assert.ok(area <= prev + 1e-9, `the area rose at t = ${(i / 24).toFixed(2)}`);
    assert.ok(area >= a1 - 1e-9 && area <= a0 + 1e-9, "and it stays between the two shapes' areas");
    prev = area;
  }
});

test("step 3 is what stops the collapse: the same 150-degree turn, vertex-locked, loses its area", () => {
  /* an asymmetric shape (a flag), so the alignment cannot be had for free by symmetry */
  const flag = (deg) => { const r = deg * Math.PI / 180, c = Math.cos(r), s = Math.sin(r);
    return [[-150, -20], [150, -60], [150, 20], [-150, 60]].map(([x, y]) => [500 + x * c - y * s, 300 + x * s + y * c]); };
  const aligned = morphAPrepare(flag(0), flag(150), { n: 64 });
  const locked = { A: resample(flag(0), 64), B: resample(flag(150), 64), offset: 0, n: 64 };   /* steps 1 and 3 skipped */
  const minArea = (prep) => { let w = Infinity; for (let i = 0; i <= 20; i++) w = Math.min(w, morphAArea(morphAAt(prep, i / 20).outline)); return w; };
  assert.ok(aligned.offset !== 0, "the turn is carried by a cyclic offset, not by the vertices' own order");
  assert.ok(minArea(locked) < 0.1 * morphAArea(locked.A), `vertex-locked, the flag collapses to ${minArea(locked).toFixed(0)} of ${morphAArea(locked.A).toFixed(0)}`);
  assert.ok(minArea(aligned) > 0.97 * morphAArea(aligned.A), "normalised and aligned, it keeps its area through the same turn");
  /* what is left for METHOD B is the turn the cyclic offset cannot absorb - which is why the compiler refuses a pair
     whose principal axes turn more than ARAP.AXIS_MAX_DEG rather than trusting either method with it */
});

test("the cubic reconstruction passes through every vertex of the lerped ring", () => {
  const prep = morphAPrepare(square(500, 300, 240), circle(500, 300, 120), { n: 32 });
  const ring = morphAAt(prep, 0.4).outline, d = morphAPath(ring);
  assert.ok(d.startsWith("M") && d.endsWith("Z"), d.slice(0, 40));
  const segs = d.split(" C").length - 1;
  assert.equal(segs, ring.length, "one cubic per edge, the ring closed");
  /* every cubic ENDS on the next knot: the curve interpolates the lerp, it does not approximate it */
  const ends = [...d.matchAll(/C[-\d. ]+? ([-\d.]+) ([-\d.]+)(?= C| Z)/g)].map((m) => [+m[1], +m[2]]);
  assert.equal(ends.length, ring.length);
  ends.forEach((p, i) => {
    const knot = ring[(i + 1) % ring.length];
    assert.ok(Math.abs(p[0] - knot[0]) < 0.05 && Math.abs(p[1] - knot[1]) < 0.05, `cubic ${i} ends off its knot`);
  });
  assert.equal(morphAPath([[1, 2]]), "M1.0 2.0", "a degenerate ring is a point, not a throw");
});

test("min det reads the fold Method A has no guarantee against - positive on a strip that does not fold", () => {
  const n = 24;
  const top = [...Array(n).keys()].map((i) => [70 + i * 30, 200 - 2 * i]);
  const top2 = [...Array(n).keys()].map((i) => [70 + i * 30, 260 + 1.5 * i]);
  const bot = [...Array(n).keys()].map((i) => [70 + i * 30, 470]);
  const mesh = stripMesh(top, bot), Bv = [...top2, ...bot];
  for (let i = 0; i <= 10; i++) {
    const verts = mesh.verts.map((p, k) => [p[0] + (Bv[k][0] - p[0]) * (i / 10), p[1] + (Bv[k][1] - p[1]) * (i / 10)]);
    assert.ok(morphAMinDet(mesh.verts, verts, mesh.tris) > 0, `a column folded at t = ${i / 10}`);
  }
  const folded = mesh.verts.map((p, k) => (k < n ? [p[0], 600] : p));   // the top edge dragged through the bottom
  assert.ok(morphAMinDet(mesh.verts, folded, mesh.tris) < 0, "and it is negative when the shape is turned inside out");
});

test("the dials are frozen and carry their reasons", () => {
  assert.equal(MORPH_A.N, 96);
  assert.equal(MORPH_A.ALPHA, 0.5);
  assert.throws(() => { MORPH_A.N = 4; }, TypeError);
  assert.throws(() => morphAPrepare(square(0, 0, 10), resample(circle(0, 0, 5), 12), { resample: false }), /vertices/);
  /* normalise: false - the caller's own order kept, step 3 still run (the strip's case: the offset is 0) */
  const top = [...Array(12).keys()].map((i) => [70 + i * 30, 200 - 3 * i]), bot = [...Array(12).keys()].map((i) => [70 + i * 30, 470]);
  const ring = (t) => [...t, ...bot.slice().reverse()];
  const p = morphAPrepare(ring(top), ring(top.map(([x, y]) => [x, y - 40])), { resample: false, normalise: false });
  assert.equal(p.offset, 0, "two strips built column by column already correspond");
  assert.deepEqual(p.A, ring(top), "and their own order is kept");
});
