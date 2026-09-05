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
