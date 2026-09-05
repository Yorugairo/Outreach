// P43 T4 - area-preserving squash (42 s42.3): det(A) == 1 across theta and alpha including alpha -> 0 and large alpha;
// alpha from speed and deceleration; the vortex's expressions unchanged to the bit; a pop's squash from its spring.
import { test } from "node:test";
import assert from "node:assert/strict";
import { SQUASH, squashAlpha, squashMatrix, det2, scaleBy, springSquash } from "../../scripts/kinetics/squash.mjs";
import { springParams, springEval } from "../../scripts/kinetics/spring.mjs";

test("47 s1: det(A(t)) == 1 within float tolerance for all theta and alpha, including alpha -> 0 and large alpha", () => {
  for (const alpha of [0, 1e-9, 1e-6, 0.01, 0.25, 1, 5, 50, 1000]) for (let k = 0; k < 48; k++) {
    const theta = k / 48 * Math.PI * 2, m = squashMatrix(theta, alpha);
    assert.ok(Math.abs(det2(m) - 1) < 1e-9, `theta ${theta} alpha ${alpha}: det ${det2(m)}`);
    assert.ok(Math.abs(m[1] - m[2]) < 1e-12, "symmetric: a pure stretch, no shear");
  }
  assert.deepEqual(squashMatrix(0.7, 0), [1, 0, 0, 1]);
});

test("the stretch is along theta: at theta = 0 x grows and y shrinks, at pi/2 the other way round", () => {
  const m0 = squashMatrix(0, 0.5), m90 = squashMatrix(Math.PI / 2, 0.5);
  assert.ok(Math.abs(m0[0] - 1.5) < 1e-12 && Math.abs(m0[3] - 1 / 1.5) < 1e-12);
  assert.ok(Math.abs(m90[3] - 1.5) < 1e-12 && Math.abs(m90[0] - 1 / 1.5) < 1e-12);
});

test("alpha is driven by speed and by deceleration only: zero at rest, an acceleration ALONG the motion adds nothing", () => {
  assert.equal(squashAlpha([0, 0], [0, 100]), 0);
  const cruise = squashAlpha([300, 0], [0, 0]), pushed = squashAlpha([300, 0], [5000, 0]), braked = squashAlpha([300, 0], [-5000, 0]);
  assert.ok(Math.abs(cruise - SQUASH.KV * 300) < 1e-12);
  assert.equal(pushed, cruise, "acceleration along v is not deceleration");
  assert.ok(braked > cruise, "deceleration adds");
  assert.ok(Math.abs(braked - (SQUASH.KV * 300 + SQUASH.KA * 5000)) < 1e-12);
  assert.equal(squashAlpha([1e6, 0], [0, 0]), SQUASH.MAX, "clamped");
  assert.equal(squashAlpha([0, 0], [0, 0], { KV: 1 }), 0);
});

test("scaleBy is the vortex's own expressions to the bit, and conserves area up to the uniform scale", () => {
  for (const s of [1, 0.73, 0.1]) for (const a of [0, 0.3, 0.85]) {
    const q = scaleBy(s, a);
    assert.equal(q.sx, s * (1 + a)); assert.equal(q.sy, s / (1 + a));
    assert.ok(Math.abs(q.sx * q.sy - s * s) < 1e-12);
  }
});

test("a pop's squash follows its spring: nothing at rest, most on the way up, small once landed", () => {
  const p = springParams(0.04), travel = 18, dur = 0.5;
  assert.equal(springSquash(0, p, travel, dur), 0);
  const mid = springSquash(0.12, p, travel, dur), landed = springSquash(1, p, travel, dur);
  assert.ok(mid > 0 && mid <= SQUASH.MAX);
  assert.ok(landed < mid * 0.1, `landed ${landed} vs mid ${mid}`);
  const v = travel * springEval(0.12, p).v / dur;
  assert.ok(Math.abs(mid - squashAlpha([0, v], [0, travel * springEval(0.12, p).a / (dur * dur)])) < 1e-15);
});
