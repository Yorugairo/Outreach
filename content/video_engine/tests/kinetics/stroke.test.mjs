// P43 T2 - the curvature-reparameterised stroke (42 s42.1). The three rows of 47 s1: the two-thirds law, the kappa0
// regulariser, the width coupling - plus rest at both ends, and the FAILING case: the template's sliding mask.
import { test } from "node:test";
import assert from "node:assert/strict";
import { menger, strokeProfile, strokeS, strokeAt, STROKE } from "../../scripts/kinetics/stroke.mjs";

// a path with one long straight, one sharp corner (a 90-degree arc of radius 6) and a second straight, ~2 px pitch
const cornerPath = (lead = 200, tail = 200, r = 6) => {
  const pts = [];
  for (let x = 0; x <= lead; x += 2) pts.push({ x, y: 0 });
  for (let k = 1; k <= 5; k++) { const a = (k / 5) * Math.PI / 2; pts.push({ x: lead + r * Math.sin(a), y: r - r * Math.cos(a) }); }
  for (let y = r + 2; y <= r + tail; y += 2) pts.push({ x: lead + r, y });
  return pts;
};
const argmax = (arr) => { let i = 0; for (let j = 1; j < arr.length; j++) if (arr[j] > arr[i]) i = j; return i; };
const argmin = (arr) => { let i = 0; for (let j = 1; j < arr.length; j++) if (arr[j] < arr[i]) i = j; return i; };

test("menger curvature is 1 / radius on a circle and 0 on a line", () => {
  const c = (a) => ({ x: 10 * Math.cos(a), y: 10 * Math.sin(a) });
  assert.ok(Math.abs(menger(c(0), c(0.3), c(0.6)) - 0.1) < 1e-9);
  assert.equal(menger({ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }), 0);
  assert.equal(menger({ x: 0, y: 0 }, { x: 0, y: 0 }, { x: 0, y: 0 }), 0);
});

test("42.1 the two-thirds law: the pen is slower at max curvature than at min curvature", () => {
  const p = strokeProfile(cornerPath());
  const hi = argmax(p.kappa), lo = argmin(p.kappa);
  assert.ok(p.kappa[hi] > p.kappa[lo]);
  assert.ok(p.v[hi] < p.v[lo], `v(max k) ${p.v[hi]} must be < v(min k) ${p.v[lo]}`);
  assert.ok(p.v[lo] / p.v[hi] > 2, `a radius-6 corner should slow the pen more than 2x on this path: ${p.v[lo] / p.v[hi]}`);
});

test("42.1 width and ink couple to the same profile: the nib pools in the corner", () => {
  const p = strokeProfile(cornerPath());
  const hi = argmax(p.kappa), lo = argmin(p.kappa);
  assert.ok(p.w[hi] > p.w[lo], `w(max k) ${p.w[hi]} must be > w(min k) ${p.w[lo]}`);
  assert.ok(Math.abs(p.w[lo] - (1 + STROKE.LAMBDA_W)) < 1e-9, "on the straight the nib is at base width + lambda_w");
});

test("42.1 kappa0: a straight path returns one finite speed everywhere and a linear clock", () => {
  const pts = []; for (let x = 0; x <= 400; x += 2) pts.push({ x, y: 0 });
  const p = strokeProfile(pts);
  for (let i = 0; i < p.n; i++) { assert.ok(Number.isFinite(p.v[i])); assert.ok(Math.abs(p.v[i] - p.vMax) < 1e-12); }
  for (let i = 0; i < p.n; i++) assert.ok(Math.abs(p.t[i] - p.s[i] / p.L) < 1e-12);
});

test("the stroke starts and ends at rest, is monotone, and lands on exactly L", () => {
  const p = strokeProfile(cornerPath()), h = 1e-4;
  assert.equal(strokeS(p, 0), 0); assert.equal(strokeS(p, 1), p.L); assert.equal(strokeS(p, 1.5), p.L);
  assert.ok((strokeS(p, h) - strokeS(p, 0)) / h < 1e-3 * p.L, "v(0) ~ 0");
  assert.ok((strokeS(p, 1) - strokeS(p, 1 - h)) / h < 1e-3 * p.L, "v(1) ~ 0");
  let prev = 0;
  for (let i = 1; i <= 500; i++) { const s = strokeS(p, i / 500); assert.ok(s >= prev); prev = s; }
});

test("the pen spends longer in the corner than the sliding mask does: velocity is a function of kappa, not of the clock", () => {
  const p = strokeProfile(cornerPath(200, 200)), h = 1e-3;
  const cornerS = p.s[argmax(p.kappa)];
  // the hand: speed (ds/du) measured where the pen passes the corner vs where it passes the middle of the tail straight
  const uAt = (S) => { let lo = 0, hi = 1; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (strokeS(p, m) < S) lo = m; else hi = m; } return (lo + hi) / 2; };
  const speed = (u) => (strokeS(p, u + h) - strokeS(p, u - h)) / (2 * h);
  const tailS = cornerS + 100;
  assert.ok(speed(uAt(cornerS)) < speed(uAt(tailS)), "hand: slower in the corner than on the straight after it");
  // the FAILING case (47 s1): the template's sliding mask, len * spEase(k) - it decelerates with the CLOCK, so it is
  // faster in the corner than on the straight that follows, whatever the geometry says
  const spEase = (k) => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3), maskS = (k) => p.L * spEase(k);
  const kAt = (S) => { let lo = 0, hi = 1; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (maskS(m) < S) lo = m; else hi = m; } return (lo + hi) / 2; };
  const maskSpeed = (k) => (maskS(k + h) - maskS(k - h)) / (2 * h);
  assert.ok(maskSpeed(kAt(cornerS)) > maskSpeed(kAt(tailS)), "mask: faster in the corner than after it - the defect");
});

test("strokeAt reads the profile at an arclength, linear between samples", () => {
  const p = strokeProfile(cornerPath());
  assert.equal(strokeAt(p, p.v, -1), p.v[0]); assert.equal(strokeAt(p, p.v, p.L + 1), p.v[p.n - 1]);
  const mid = (p.s[3] + p.s[4]) / 2;
  assert.ok(Math.abs(strokeAt(p, p.v, mid) - (p.v[3] + p.v[4]) / 2) < 1e-12);
});
