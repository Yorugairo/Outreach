// P43 T1 + T5 - the spring (42 s42.2): the shipping pop pinned to the bit, then the three regimes with velocity and
// acceleration, the inverse model's peak, and the SEEK test an integrator fails by construction (47 s1 row 4).
import { test } from "node:test";
import assert from "node:assert/strict";
import { SPRING, springParams, springEval, springPop, POP } from "../../scripts/kinetics/spring.mjs";

// the 2026-09-05 shipping formula, verbatim - springPop must return these exact bits
const shipped = (u, Mp = 0.04) => {
  if (u >= 1) return 1; if (u <= 0) return 0;
  const L = Math.log(Mp), z = -L / Math.sqrt(Math.PI * Math.PI + L * L), w = 6 / z, wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * u) * (Math.cos(wd * u) + (z * w / wd) * Math.sin(wd * u));
};
const dnum = (f, t, h = 1e-6) => (f(t + h) - f(t - h)) / (2 * h);

test("springPop is bit-identical to the shipping formula at Mp 0.04, and lands on exactly 1 / starts at exactly 0", () => {
  for (let i = 0; i <= 2000; i++) { const u = i / 2000; assert.equal(springPop(u), shipped(u), `u=${u}`); }
  for (const Mp of [0.1, 0.2]) for (let i = 1; i < 50; i++) assert.equal(springPop(i / 50, Mp), shipped(i / 50, Mp));
  assert.equal(springPop(1), 1); assert.equal(springPop(2), 1); assert.equal(springPop(0), 0); assert.equal(springPop(-1), 0);
});

test("the inverse model holds: the peak is exactly 1 + Mp at t_p = pi / wd, inside the pop; zeta * w = the settle", () => {
  for (const Mp of [0.04, 0.1, 0.3]) {
    const p = springParams(Mp), tp = Math.PI / p.wd;
    assert.ok(tp < 1, `t_p ${tp} lands before the pop ends`);
    assert.ok(Math.abs(springEval(tp, p).x - (1 + Mp)) < 1e-9, `Mp ${Mp}: peak ${springEval(tp, p).x}`);
    assert.ok(Math.abs(springEval(tp, p).v) < 1e-9, "velocity is zero at the peak");
    assert.ok(Math.abs(p.z * p.w - SPRING.SETTLE) < 1e-12);
  }
  assert.ok(Math.abs(springPop(0.999) - 1) < 0.004, "the envelope is at 0.25% by the end");
  assert.equal(POP.z, springParams(0.04).z);
});

test("zeta = 1 overshoots zero and still arrives; zeta > 1 is monotone and never crosses 1", () => {
  const crit = springParams(0), over = { z: 1.6, w: 6 };
  assert.equal(crit.z, 1);
  let prev = 0;
  for (const p of [crit, over]) {
    prev = 0;
    for (let i = 1; i <= 2000; i++) { const x = springEval(i / 1000, p).x; assert.ok(x <= 1 + 1e-12, `no overshoot: ${x}`); assert.ok(x >= prev - 1e-12, "monotone"); prev = x; }
    assert.ok(springEval(1, p).x > 0.85 && springEval(4, p).x > 0.999, `arrives: x(1) ${springEval(1, p).x} (an overdamped spring is slower to settle)`);
  }
});

test("velocity and acceleration are the derivatives of position in all three regimes, and rest at t = 0", () => {
  for (const p of [springParams(0.04), springParams(0), { z: 1.6, w: 6 }]) {
    const x = (t) => springEval(t, p).x, v = (t) => springEval(t, p).v;
    for (const t of [0.05, 0.2, 0.5, 0.9]) {
      assert.ok(Math.abs(springEval(t, p).v - dnum(x, t)) < 1e-6, `v(${t}) z=${p.z}`);
      assert.ok(Math.abs(springEval(t, p).a - dnum(v, t)) < 1e-4, `a(${t}) z=${p.z}`);
    }
    assert.deepEqual(springEval(0, p), { x: 0, v: 0, a: 0 });
  }
});

test("THE SEEK TEST: frame N evaluated directly equals frames 0..N stepped, bit-identical; an integrator cannot", () => {
  const p = springParams(0.04), N = 37, dt = 1 / 60;
  let stepped = null;
  for (let n = 0; n <= N; n++) stepped = springEval(n * dt, p).x;
  assert.equal(stepped, springEval(N * dt, p).x);
  // the contrast: a semi-implicit Euler spring reaches a DIFFERENT frame N when the frames it was stepped through differ
  const euler = (steps, h) => { let x = 0, v = 0; for (let i = 0; i < steps; i++) { v += (-2 * p.z * p.w * v - p.w * p.w * (x - 1)) * h; x += v * h; } return x; };
  const coarse = euler(N, dt), fine = euler(N * 4, dt / 4);
  assert.notEqual(coarse, fine, "an integrator's frame N depends on the path taken to it - the defect");
  assert.ok(Math.abs(fine - springEval(N * dt, p).x) < 0.02, "and it only approximates the closed form");
});
