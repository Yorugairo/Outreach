// P47 T3 / P38 T5 - the morph (43 s43.5): Method A's resample + rotational alignment, and Method B's ARAP - the
// closed-form polar decomposition, the interpolation on SO(2) x Sym+(2) with det J(t) > 0 at every t where the naive
// vertex lerp collapses, the factored global step, and the three match-cut invariants (the brief B4).
import { test } from "node:test";
import assert from "node:assert/strict";
import { ARAP, polyArea, centroid, resample, alignOffset, rotate, correspond, lerpShape, fanMesh, triJacobian, det2x2, polar,
         jacobianAt, arapPrepare, arapAt, minDet, dominantAxis, bbox, morphInvariants, outlinePath, stripMesh, stripOutline, arapPrepareMesh } from "../../scripts/kinetics/arap.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const rect = (cx, cy, w, h, deg = 0) => {   /* a rectangle outline, rotated, counter-clockwise */
  const r = deg * Math.PI / 180, c = Math.cos(r), s = Math.sin(r);
  return [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]].map(([x, y]) => [cx + x * c - y * s, cy + x * s + y * c]);
};
const square = rect(500, 300, 240, 240);

test("resample: n equal-arc vertices, counter-clockwise, the area kept", () => {
  const R = resample(square, 48);
  assert.equal(R.length, 48);
  assert.ok(polyArea(R) > 0 && near(polyArea(R), 240 * 240, 1e-6), "a square resampled on its own edges keeps its area");
  const cw = square.slice().reverse();
  assert.ok(polyArea(resample(cw, 48)) > 0, "a clockwise outline is turned counter-clockwise");
  const seg = R.map((p, i) => Math.hypot(R[(i + 1) % 48][0] - p[0], R[(i + 1) % 48][1] - p[1]));
  assert.ok(Math.max(...seg) - Math.min(...seg) < 1e-6, "equal arc length");
});

test("rotational alignment finds the cyclic offset of a rotated copy, so the correspondence never twists", () => {
  const A = resample(square, 40), B = rotate(A, 13);
  assert.equal(alignOffset(A, B), (40 - 13) % 40);
  const { A: a2, B: b2 } = correspond(square, rect(900, 300, 240, 240));   /* the same square, elsewhere: aligned by shape, not position */
  const d = a2.reduce((s, p, i) => s + Math.hypot(p[0] - (b2[i][0] - 400), p[1] - b2[i][1]), 0);
  assert.ok(d < 1e-6, "vertex i of A corresponds to vertex i of B once translation is removed");
});

test("the polar decomposition is closed-form and exact: J = R S with S symmetric, det J = det S", () => {
  const J = [[1.4, 0.3], [-0.9, 0.8]];
  const { theta, S } = polar(J);
  assert.ok(near(S[0][1], S[1][0], 1e-12), "S is symmetric");
  const c = Math.cos(theta), s = Math.sin(theta);
  const RS = [[c * S[0][0] - s * S[1][0], c * S[0][1] - s * S[1][1]], [s * S[0][0] + c * S[1][0], s * S[0][1] + c * S[1][1]]];
  for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) assert.ok(near(RS[i][j], J[i][j], 1e-12));
  assert.ok(near(jacobianAt(J, 0)[0][0], 1) && near(jacobianAt(J, 0)[1][1], 1) && near(jacobianAt(J, 0)[0][1], 0), "t = 0 is the identity");
  const J1 = jacobianAt(J, 1);
  for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) assert.ok(near(J1[i][j], J[i][j], 1e-9), "t = 1 is J");
});

test("a shape turned 150 degrees, vertex-locked: the naive lerp collapses to a sliver, ARAP keeps det J(t) > 0 at every t", () => {
  /* the doc's claim (43 s43.5): past 90 degrees of rotation the vertex lerp collapses - at 150 degrees the mid-frame is scaled by
     cos(75 deg) = 0.26 in every direction, a sliver; ARAP interpolates the rotation on SO(2) and the shape never thins */
  const L = [[400, 200], [640, 200], [640, 260], [470, 260], [470, 420], [400, 420]];   /* an L, not symmetric under a half turn */
  const A = resample(L, 60), cA = centroid(A), th = 150 * Math.PI / 180, c = Math.cos(th), s = Math.sin(th);
  const B = A.map(([x, y]) => [cA[0] + (x - cA[0]) * c - (y - cA[1]) * s, cA[1] + (x - cA[0]) * s + (y - cA[1]) * c]);   /* index-locked: vertex i -> its rotated self */
  let minArea = Infinity;
  for (let i = 0; i <= 40; i++) minArea = Math.min(minArea, polyArea(lerpShape(A, B, i / 40)));
  assert.ok(minArea < 0.1 * polyArea(A), `the lerp's area collapses to ${minArea.toFixed(0)} of ${polyArea(A).toFixed(0)}`);
  const prepL = arapPrepare(A, B);
  let worstL = Infinity, minAreaL = Infinity;
  for (let i = 0; i <= 40; i++) { const d = minDet(prepL, i / 40); worstL = Math.min(worstL, d.target, d.solved); minAreaL = Math.min(minAreaL, polyArea(arapAt(prepL, i / 40).outline)); }
  assert.ok(worstL > 0, `ARAP: every Jacobian and every solved triangle keeps det > 0 through 150 degrees (worst ${worstL})`);
  assert.ok(minAreaL > 0.9 * polyArea(A), `ARAP: a pure rotation keeps the area (min ${minAreaL.toFixed(0)} of ${polyArea(A).toFixed(0)})`);
});

test("a square into a thin bar through 120 degrees (the morph we ship): ARAP keeps det J(t) > 0 and the area, ends on the ends", () => {
  const bar = rect(560, 320, 420, 60, 120);
  const { A, B } = correspond(square, bar, 64);
  /* METHOD B never inverts: the interpolated Jacobians by construction, and the solved mesh in practice */
  const prep = arapPrepare(A, B);
  let worstTarget = Infinity, worstSolved = Infinity, minAreaB = Infinity;
  for (let i = 0; i <= 40; i++) {
    const t = i / 40, d = minDet(prep, t);
    worstTarget = Math.min(worstTarget, d.target); worstSolved = Math.min(worstSolved, d.solved);
    minAreaB = Math.min(minAreaB, polyArea(arapAt(prep, t).outline));
  }
  assert.ok(worstTarget > 0, `every interpolated Jacobian has det > 0 (worst ${worstTarget})`);
  assert.ok(worstSolved > 0, `no triangle of the solved mesh inverts (worst ${worstSolved})`);
  assert.ok(minAreaB > 0.6 * Math.min(polyArea(A), polyArea(B)), `the ARAP outline keeps its area (min ${minAreaB.toFixed(0)})`);
  /* the ends are the ends */
  const s0 = arapAt(prep, 0).outline, s1 = arapAt(prep, 1).outline;
  assert.ok(s0.every((p, i) => Math.hypot(p[0] - A[i][0], p[1] - A[i][1]) < 1e-6), "t = 0 is the source");
  assert.ok(s1.every((p, i) => Math.hypot(p[0] - B[i][0], p[1] - B[i][1]) < 1e-3), "t = 1 is the target");
  assert.deepEqual(arapAt(prep, 0.37).outline, arapAt(prep, 0.37).outline, "pure");
});

test("the fan mesh and a triangle's Jacobian: a pure rotation of the rest mesh gives R with S = I", () => {
  const A = resample(square, 12), M = fanMesh(A);
  assert.equal(M.verts.length, 13); assert.equal(M.tris.length, 12);
  const th = 0.7, c = Math.cos(th), s = Math.sin(th), rot = (p) => [c * p[0] - s * p[1], s * p[0] + c * p[1]];
  const [i, j, k] = M.tris[3], J = triJacobian(M.verts[i], M.verts[j], M.verts[k], rot(M.verts[i]), rot(M.verts[j]), rot(M.verts[k]));
  const p = polar(J);
  assert.ok(near(p.theta, th, 1e-9) && near(p.S[0][0], 1, 1e-9) && near(p.S[1][1], 1, 1e-9) && near(p.S[0][1], 0, 1e-9));
  assert.ok(near(det2x2(J), 1, 1e-9));
});

test("the match-cut invariants: a morph that stays put passes, one that walks off or turns fails by name", () => {
  const W = 1920;
  const good = [square, rect(510, 310, 260, 200), rect(520, 320, 300, 180, 8)];
  const g = morphInvariants(good, W);
  assert.ok(g.centroid_ok && g.axis_ok && g.area_ok, JSON.stringify(g));
  const walked = morphInvariants([square, rect(900, 300, 240, 240)], W);
  assert.ok(!walked.centroid_ok && walked.centroid_shift > 0.2, "a 400 px walk breaks the centroid invariant");
  const turned = morphInvariants([rect(500, 300, 400, 100), rect(500, 300, 400, 100, 40)], W);
  assert.ok(!turned.axis_ok && Math.abs(turned.axis_deg - 40) < 1e-6, "a 40 degree turn breaks the axis invariant");
  const shrunk = morphInvariants([square, rect(500, 300, 240, 240), rect(500, 300, 100, 100)], W);
  assert.ok(!shrunk.area_ok && near(shrunk.area_ratio, 100 * 100 / (240 * 240), 1e-9), "a collapse breaks the area invariant");
  assert.ok(near(dominantAxis(rect(0, 0, 400, 100, 30)), 30 * Math.PI / 180, 1e-9), "the dominant axis is the long axis");
  assert.deepEqual(bbox([[0, 0], [10, 5]]), { x: 0, y: 0, w: 10, h: 5 });
  assert.deepEqual(Object.keys(ARAP), ["N", "CENTROID_MAX", "AXIS_MAX_DEG", "AREA_MIN_RATIO"]);
});

test("outlinePath writes fixed decimals and closes", () => {
  assert.equal(outlinePath([[0, 0], [10.234, 0], [10, 5.5]]), "M0.0 0.0 L10.2 0.0 L10.0 5.5 Z");
  assert.deepEqual(centroid([[0, 0], [2, 0], [2, 2], [0, 2]]), [1, 1]);
});

test("the strip: a tab becomes the area under a jagged series with no triangle inverting, where a fan flips", () => {
  /* a series with deep dips and a steep spike, on a 1000 x 560 board: the area under it is not star-shaped */
  const n = 48, xs = [...Array(n).keys()].map((i) => 70 + i * (710 / (n - 1)));
  const ys = xs.map((x, i) => 470 - 120 - 200 * Math.abs(Math.sin(i / 3.1)) - (i > 30 && i < 34 ? 120 : 0) - (i === 20 ? 90 : 0));
  const topB = xs.map((x, i) => [x, ys[i]]), botB = xs.map((x) => [x, 470]);
  const cx = 425, cy = 330, w = 0.9 * 710, h = 0.75 * 410;   /* the tab: a strip of the same n columns, sized as the template sizes it (TAB_W / TAB_H of the target's box) */
  const topA = xs.map((x, i) => [cx - w / 2 + (i / (n - 1)) * w, cy - h / 2 + (i >= n - 2 ? 12 : 0)]);
  const botA = xs.map((x, i) => [cx - w / 2 + (i / (n - 1)) * w, cy + h / 2 - (i >= n - 2 ? 12 : 0)]);
  const mesh = stripMesh(topA, botA), prep = arapPrepareMesh(mesh, [...topB, ...botB], n + (n >> 1));
  assert.equal(prep.strip, n);
  let worst = Infinity;
  for (let i = 0; i <= 24; i++) { const d = minDet(prep, i / 24); worst = Math.min(worst, d.target, d.solved); }
  assert.ok(worst > 0, `strip: every target Jacobian and every solved triangle keeps det > 0 (worst ${worst})`);
  const end = arapAt(prep, 1).outline, want = stripOutline([...topB, ...botB], n);
  assert.ok(end.every((p, i) => Math.hypot(p[0] - want[i][0], p[1] - want[i][1]) < 1e-3), "t = 1 is the area under the series");
  const inv = morphInvariants([...Array(25).keys()].map((i) => arapAt(prep, i / 24).outline), 1000);
  assert.ok(inv.centroid_ok && inv.area_ok, JSON.stringify(inv));
  /* the fan on the same target inverts: the proof the strip is needed */
  const outlineB = stripOutline([...topB, ...botB], n);
  const { A, B } = correspond(stripOutline([...topA, ...botA], n), outlineB, 96);
  const fan = arapPrepare(A, B, { centre: [centroid(B)[0], 470 - 6] });
  const V = fan.mesh.verts, Bv = [...B, [centroid(B)[0], 470 - 6]];
  const flipped = fan.mesh.tris.filter(([i, j, k]) => det2x2(triJacobian(V[i], V[j], V[k], Bv[i], Bv[j], Bv[k])) <= 0).length;
  assert.ok(flipped > 0, "the fan flips at least one triangle on a jagged series (why the strip exists)");
});
