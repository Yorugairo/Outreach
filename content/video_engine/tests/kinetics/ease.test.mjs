// P43 T1 - the first test that reaches the template's math. Pins minJerk (FINDING s2): rest at both ends.
import { test } from "node:test";
import assert from "node:assert/strict";
import { minJerk } from "../../scripts/kinetics/ease.mjs";

// one-sided differences AT the ends (a central difference would sample outside [0,1], where the clamp flattens everything)
const fwd1 = (f, u, h) => (f(u + h) - f(u)) / h, bwd1 = (f, u, h) => (f(u) - f(u - h)) / h;
const fwd2 = (f, u, h) => (f(u + 2 * h) - 2 * f(u + h) + f(u)) / (h * h), bwd2 = (f, u, h) => (f(u) - 2 * f(u - h) + f(u - 2 * h)) / (h * h);

test("minJerk is pinned at the ends and clamps outside [0,1]", () => {
  assert.equal(minJerk(0), 0); assert.equal(minJerk(1), 1);
  assert.equal(minJerk(-3), 0); assert.equal(minJerk(7), 1);
  assert.equal(minJerk(0.5), 0.5);
});

test("minJerk starts and ends at rest: zero velocity AND zero acceleration at both ends", () => {
  const h = 1e-5;   // the truncation error of the 2nd difference is f'''(0) h = 60 h = 6e-4
  assert.ok(Math.abs(fwd1(minJerk, 0, h)) < 1e-8, "v(0)");
  assert.ok(Math.abs(bwd1(minJerk, 1, h)) < 1e-8, "v(1)");
  assert.ok(Math.abs(fwd2(minJerk, 0, h)) < 1e-3, `a(0) = ${fwd2(minJerk, 0, h)}`);
  assert.ok(Math.abs(bwd2(minJerk, 1, h)) < 1e-3, `a(1) = ${bwd2(minJerk, 1, h)}`);
  // the contrast that makes the test mean something: the template's quadratic io starts with a = 4
  const io = (k) => k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
  assert.ok(Math.abs(fwd2(io, 0, h) - 4) < 1e-6, `io a(0) = ${fwd2(io, 0, h)}`);
});

test("minJerk is monotone and symmetric about the midpoint", () => {
  let prev = 0;
  for (let i = 1; i <= 200; i++) { const v = minJerk(i / 200); assert.ok(v >= prev); prev = v; }
  for (const u of [0.1, 0.25, 0.4]) assert.ok(Math.abs(minJerk(u) + minJerk(1 - u) - 1) < 1e-12);
});

// P69 T26d: the Hermite path through keys (ported from rig_math.py `hermite`, d154278) - a prop's chained moves
import { hermite, hermiteChain } from "../../scripts/kinetics/ease.mjs";

test("hermite hits its ends and leaves / arrives at its stated velocities", () => {
  const h = 1e-6, T = 2, f = (u) => hermite(10, 50, 7, -3, u, T);
  assert.equal(f(0), 10); assert.equal(f(1), 50);
  assert.ok(Math.abs((f(h) - f(0)) / h / T - 7) < 1e-4, "v(0) = v0 (per second, over T)");
  assert.ok(Math.abs((f(1) - f(1 - h)) / h / T - -3) < 1e-4, "v(1) = v1");
  assert.equal(hermite(10, 50, 0, 0, 0.5, T), 30, "zero end velocities: the smoothstep, symmetric");
  assert.equal(f(-1), 10); assert.equal(f(4), 50);
});

test("hermiteChain passes THROUGH a middle key at speed and settles only at the last", () => {
  const ps = [0, 100, 300], ts = [0, 1, 2], h = 1e-6;
  assert.equal(hermiteChain(ps, ts, -1), 0); assert.equal(hermiteChain(ps, ts, 0), 0);
  assert.equal(hermiteChain(ps, ts, 1), 100); assert.equal(hermiteChain(ps, ts, 2), 300); assert.equal(hermiteChain(ps, ts, 9), 300);
  const vMid = (hermiteChain(ps, ts, 1 + h) - hermiteChain(ps, ts, 1 - h)) / (2 * h);
  assert.ok(Math.abs(vMid - 150) < 1e-3, `the middle key is crossed at the Catmull-Rom velocity 150 u/s, not 0: ${vMid}`);
  assert.ok(Math.abs((hermiteChain(ps, ts, h) - 0) / h) < 1e-3, "starts from rest");
  assert.ok(Math.abs((300 - hermiteChain(ps, ts, 2 - h)) / h) < 1e-3, "settles at the last key");
  const left = (hermiteChain(ps, ts, 1) - hermiteChain(ps, ts, 1 - h)) / h, right = (hermiteChain(ps, ts, 1 + h) - hermiteChain(ps, ts, 1)) / h;
  assert.ok(Math.abs(left - right) < 1e-2, "C1 across the middle key: no kink");
  assert.equal(hermiteChain([5, 9], [0, 1], 0.5), 7, "one segment, rest at both ends: the smoothstep");
});
