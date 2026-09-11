// P50 T14 - THE CLOTHOID FITTER (doc 42 s42.4). The law is dk/ds = const, and everything below is a way of
// asking whether that is what came out: the curvature measured ON THE SAMPLES is a straight line in arclength
// and monotone; the two ends are hit, in position and in heading; the two-segment S-fit is G2 at its join; and
// the cubic Bezier over the SAME two ends throws the parasitic inflection the doc names, where the clothoid
// holds one sign. Pure functions - no clock, no randomness, no state.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CLOTHOID, fresnel, fresnelMoments, wrapPi, angleOf, clothoidFit, clothoidAt, clothoid, clothoidS,
         bezierOf, curvatureOf, clothoidPath } from "../../scripts/kinetics/clothoid.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
/* the reference every quadrature below is judged against: a dense composite Simpson, slow and obvious */
const quad = (f, a, b, n = 200000) => {
  const h = (b - a) / n;
  let s = f(a) + f(b);
  for (let i = 1; i < n; i++) s += (i & 1 ? 4 : 2) * f(a + i * h);
  return s * h / 3;
};

test("the dials are the fitter's, and each one is a real window", () => {
  assert.ok(CLOTHOID.SERIES_R > 0 && CLOTHOID.SMALL_A > 0 && CLOTHOID.SAMPLES >= 8);
  assert.ok(CLOTHOID.BISECT >= 60, "a bracket has to be halved to the last bit, not nearly");
  assert.ok(CLOTHOID.BEZ_HANDLE > 0 && CLOTHOID.BEZ_HANDLE < 1, "the reference cubic's handle is a share of the chord");
  assert.ok(CLOTHOID.JOIN_AT > 0 && CLOTHOID.JOIN_AT < 1);
});

// ---------------------------------------------------------------- the Fresnel integrals
test("C and S are the Fresnel integrals - their tabulated values, their oddness, and their tail", () => {
  assert.ok(near(fresnel(1).C, 0.7798934003768228, 1e-12), fresnel(1).C);
  assert.ok(near(fresnel(1).S, 0.4382591473903548, 1e-12), fresnel(1).S);
  assert.ok(near(fresnel(0).C, 0) && near(fresnel(0).S, 0));
  for (const x of [0.4, 1.3, 2.7, 5.5]) {   // odd in x
    assert.ok(near(fresnel(-x).C, -fresnel(x).C, 1e-15), x);
    assert.ok(near(fresnel(-x).S, -fresnel(x).S, 1e-15), x);
  }
  for (const x of [12, 40]) {   // both tend to 1/2 (the Cornu spiral's eye)
    assert.ok(Math.abs(fresnel(x).C - 0.5) < 0.03 && Math.abs(fresnel(x).S - 0.5) < 0.03, x);
  }
});

test("the series and the asymptotic form agree at the seam, and both agree with brute-force quadrature", () => {
  const e = 1e-9, R = CLOTHOID.SERIES_R;
  assert.ok(Math.abs(fresnel(R - e).C - fresnel(R + e).C) < 1e-8, "C is continuous across SERIES_R");
  assert.ok(Math.abs(fresnel(R - e).S - fresnel(R + e).S) < 1e-8, "S is continuous across SERIES_R");
  for (const x of [0.5, 1.0, 2.0, 3.0, 4.0, 6.0]) {
    const C = quad((t) => Math.cos(Math.PI / 2 * t * t), 0, x, 20000);
    const S = quad((t) => Math.sin(Math.PI / 2 * t * t), 0, x, 20000);
    assert.ok(Math.abs(fresnel(x).C - C) < 1e-8, `C(${x}) ${fresnel(x).C} vs ${C}`);
    assert.ok(Math.abs(fresnel(x).S - S) < 1e-8, `S(${x}) ${fresnel(x).S} vs ${S}`);
  }
});

test("the generalised momenta are the integrals they claim to be - on both branches", () => {
  for (const [a, b, c] of [[1, 0, 0], [2.3, -1.1, 0.4], [-3.2, 0.7, -0.9], [12, -6, 1],
                           [0, 1.2, 0.3], [1e-9, -2.0, 0.5], [0.2, 5.0, -1.0]]) {
    const m = fresnelMoments(a, b, c);
    const X = quad((t) => Math.cos(a * t * t + b * t + c), 0, 1, 20000);
    const Y = quad((t) => Math.sin(a * t * t + b * t + c), 0, 1, 20000);
    assert.ok(Math.abs(m.X - X) < 1e-9, `X(${a},${b},${c}) ${m.X} vs ${X}`);
    assert.ok(Math.abs(m.Y - Y) < 1e-9, `Y(${a},${b},${c}) ${m.Y} vs ${Y}`);
  }
});

test("an angle is read from a number, a pair or a vector, and folded into (-pi, pi]", () => {
  assert.equal(angleOf(0.7), 0.7);
  assert.ok(near(angleOf([0, 1]), Math.PI / 2));
  assert.ok(near(angleOf({ x: -1, y: 0 }), Math.PI));
  assert.ok(near(wrapPi(3 * Math.PI), Math.PI) || near(wrapPi(3 * Math.PI), -Math.PI));
  assert.ok(near(wrapPi(-3.5 * Math.PI), 0.5 * Math.PI));
});

// ---------------------------------------------------------------- the fit meets both ends
const PAIRS = [
  [[0, 0], 0, [100, 40], 0.9],
  [[0, 0], 0.4, [200, -60], -0.3],
  [[0, 0], -1.1, [150, 150], 1.2],
  [[300, 200], 2.4, [10, -50], -2.0],
  [[0, 0], 0.001, [100, 0.0001], -0.001],
];

test("the two END TANGENTS are met - to 1e-6 and far past it - and so are the two end POINTS", () => {
  for (const [p0, t0, p1, t1] of PAIRS) {
    const f = clothoidFit(p0, t0, p1, t1);
    assert.ok(f.ok, JSON.stringify([p0, t0, p1, t1]));
    const a = clothoidAt(f, 0), b = clothoidAt(f, 1);
    assert.ok(near(a.x, p0[0], 1e-9) && near(a.y, p0[1], 1e-9), "it starts where it was told to");
    assert.ok(Math.hypot(b.x - p1[0], b.y - p1[1]) < 1e-6, `end point off by ${Math.hypot(b.x - p1[0], b.y - p1[1])}`);
    assert.ok(Math.abs(wrapPi(a.theta - t0)) < 1e-6, "the start tangent");
    assert.ok(Math.abs(wrapPi(b.theta - t1)) < 1e-6, "the end tangent");
  }
});

test("a SYMMETRIC pair is the circular arc: dk/ds is zero and the curvature never moves", () => {
  const f = clothoidFit([0, 0], 0.6, [100, 0], -0.6);   // phi1 = -phi0 - the one case with a closed form
  assert.ok(f.ok);
  assert.ok(Math.abs(f.A) < 1e-9, `A = ${f.A} - the arc is A = 0`);
  assert.ok(Math.abs(f.dk) < 1e-12, `dk = ${f.dk}`);
  const k = clothoid([0, 0], 0.6, [100, 0], -0.6, 64).map((p) => p.k);
  assert.ok(Math.max(...k) - Math.min(...k) < 1e-12, "constant curvature");
  assert.ok(near(1 / Math.abs(k[0]), 100 / (2 * Math.sin(0.6)), 1e-6), "... and it is the radius the chord and the angle imply");
});

// ---------------------------------------------------------------- dk/ds = const, measured on the samples
test("the curvature is a STRAIGHT LINE in arclength - dk/ds constant - and monotone along the segment", () => {
  const pts = clothoid([0, 0], 0.4, [200, -60], -0.3, 200);
  const k = curvatureOf(pts);
  let worst = 0;
  for (let i = 1; i < pts.length - 1; i++) worst = Math.max(worst, Math.abs(k[i] - pts[i].k));
  assert.ok(worst < 1e-9, `measured vs analytic curvature: ${worst}`);
  const dir = Math.sign(k[2] - k[1]);
  assert.notEqual(dir, 0, "pick a pair that actually turns");
  for (let i = 2; i < pts.length - 1; i++) {
    assert.ok(Math.sign(k[i] - k[i - 1]) === dir || Math.abs(k[i] - k[i - 1]) < 1e-12,
              `not monotone at ${i}: ${k[i - 1]} -> ${k[i]}`);
  }
  /* dk/ds itself: the same number between every pair of samples */
  const rate = [];
  for (let i = 2; i < pts.length - 2; i++) rate.push((pts[i + 1].k - pts[i].k) / (pts[i + 1].s - pts[i].s));
  assert.ok(Math.max(...rate) - Math.min(...rate) < 1e-12, "dk/ds is not constant");
  assert.ok(near(rate[0], clothoidFit([0, 0], 0.4, [200, -60], -0.3).dk, 1e-12));
});

test("the samples march by arclength: s is 0 at the head, L at the tail, and evenly spaced in between", () => {
  const f = clothoidFit([0, 0], -1.1, [150, 150], 1.2), pts = clothoid([0, 0], -1.1, [150, 150], 1.2, 33);
  assert.equal(pts[0].s, 0);
  assert.ok(near(pts[pts.length - 1].s, f.L, 1e-9));
  for (let i = 1; i < pts.length; i++) assert.ok(near(pts[i].s - pts[i - 1].s, f.L / 32, 1e-9), i);
  /* ... and the chord between two samples is the arclength between them, to the sampling's own error */
  for (let i = 1; i < pts.length; i++) {
    const d = Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
    assert.ok(d <= f.L / 32 + 1e-9 && d > 0.97 * f.L / 32, `${i}: chord ${d} vs step ${f.L / 32}`);
  }
});

// ---------------------------------------------------------------- the S-curve, G2 at the join
test("clothoidS is TWO segments that meet G2: same point, same heading, SAME CURVATURE at the join", () => {
  for (const [p0, t0, p1, t1] of [[[0, 0], -0.9, [300, 0], 0.9], [[0, 0], 1.0, [260, -80], 1.1], [[0, 0], -0.5, [200, 120], 0.7]]) {
    const S = clothoidS(p0, t0, p1, t1, 121);
    assert.ok(S.ok, `no curvature match found for ${JSON.stringify([t0, t1])}`);
    assert.equal(S.fits.length, 2);
    const [f1, f2] = S.fits;
    const end1 = clothoidAt(f1, 1), start2 = clothoidAt(f2, 0);
    assert.ok(near(end1.x, start2.x, 1e-9) && near(end1.y, start2.y, 1e-9), "G0 at the join");
    assert.ok(Math.abs(wrapPi(end1.theta - start2.theta)) < 1e-9, "G1 at the join");
    assert.ok(Math.abs(S.join.k_in - S.join.k_out) < 1e-9, `G2 at the join: ${S.join.k_in} vs ${S.join.k_out}`);
    const last = S.pts[S.pts.length - 1];
    assert.ok(Math.hypot(last.x - p1[0], last.y - p1[1]) < 1e-6, "and it still lands on the far end");
    assert.ok(Math.abs(wrapPi(last.theta - t1)) < 1e-6, "... facing the way it was asked to");
    /* the join is the chord's midpoint by JOIN_AT, and the arclengths run on across it */
    assert.ok(near(end1.x, p0[0] + (p1[0] - p0[0]) * CLOTHOID.JOIN_AT, 1e-6));
    for (let i = 1; i < S.pts.length; i++) assert.ok(S.pts[i].s >= S.pts[i - 1].s - 1e-12, `s went backwards at ${i}`);
  }
});

// ---------------------------------------------------------------- the defect 42 s42.4 names
test("the CUBIC over the same two ends throws the parasitic inflection; the clothoid holds one sign", () => {
  const P0 = [0, 0], P1 = [200, 0], t0 = -0.8, t1 = 0.4;
  const kc = curvatureOf(clothoid(P0, t0, P1, t1, 240)).slice(3, -3);
  const kb = curvatureOf(bezierOf(P0, t0, P1, t1, 240)).slice(3, -3);
  const sgn = (arr) => new Set(arr.filter((v) => Math.abs(v) > 1e-8).map(Math.sign));
  assert.equal(sgn(kc).size, 1, `the clothoid changed sign: ${[...sgn(kc)]}`);
  assert.equal(sgn(kb).size, 2, `the cubic did NOT ripple - pick another pair: ${[...sgn(kb)]}`);
  assert.ok(Math.min(...kb) < 0 && Math.max(...kb) > 0, "the cubic's curvature crosses zero inside the span");
  /* and the ripple is not an artefact of the handle: the cubic's curvature is not monotone at a third either,
     where the clothoid's is a straight line by construction */
  const kb3 = curvatureOf(bezierOf(P0, t0, P1, t1, 240, 1 / 3)).slice(3, -3);
  let turns = 0;
  for (let i = 2; i < kb3.length; i++) if (Math.sign(kb3[i] - kb3[i - 1]) !== Math.sign(kb3[i - 1] - kb3[i - 2])) turns++;
  assert.ok(turns > 0, "the cubic's curvature should not be monotone");
});

test("the measured curvature is SIGNED - a left turn and a right turn do not read the same", () => {
  const left = curvatureOf(clothoid([0, 0], 0.5, [200, 0], -0.5, 60));
  const right = curvatureOf(clothoid([0, 0], -0.5, [200, 0], 0.5, 60));
  assert.ok(left[10] * right[10] < 0, "mirror images must carry opposite signs");
  assert.ok(near(left[10], -right[10], 1e-12));
  assert.deepEqual(curvatureOf([{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }]), [0, 0, 0], "a straight line has none");
});

// ---------------------------------------------------------------- degenerate input, and purity
test("a degenerate pair is refused rather than drawn as NaN", () => {
  const same = clothoidFit([50, 50], 0.3, [50, 50], 1.2);
  assert.equal(same.ok, false);
  assert.ok(Number.isFinite(same.L) && Number.isFinite(same.k0) && Number.isFinite(same.dk));
  for (const p of clothoid([50, 50], 0.3, [50, 50], 1.2, 8)) assert.ok(Number.isFinite(p.x) && Number.isFinite(p.y));
  const back = clothoidFit([0, 0], 0, [100, 0], Math.PI);   // asked to turn a half circle onto its own chord
  assert.ok(Number.isFinite(back.L));
});

test("a seek IS the play: the same arguments give the same bits, in any order, with nothing remembered", () => {
  const args = [[0, 0], 0.4, [200, -60], -0.3];
  const forward = [], backward = [];
  for (let i = 0; i <= 100; i++) forward.push(JSON.stringify(clothoidAt(clothoidFit(...args), i / 100)));
  for (let i = 100; i >= 0; i--) backward.unshift(JSON.stringify(clothoidAt(clothoidFit(...args), i / 100)));
  assert.deepEqual(backward, forward);
  assert.equal(JSON.stringify(clothoid(...args, 101)[37]), forward[37]);
});

test("nothing in the module reaches for a clock or a random", () => {
  const src = [clothoidFit, clothoidAt, clothoid, clothoidS, bezierOf, curvatureOf, fresnel, fresnelMoments]
    .map((f) => f.toString()).join("\n");
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});

test("the polyline hands the nib a path, at two decimals, in order", () => {
  const d = clothoidPath(clothoid([0, 0], 0.4, [200, -60], -0.3, 5));
  assert.match(d, /^M0\.00 0\.00 L/);
  assert.equal(d.split(" L").length, 5, d);
  assert.ok(!/NaN|undefined/.test(d), d);
});
