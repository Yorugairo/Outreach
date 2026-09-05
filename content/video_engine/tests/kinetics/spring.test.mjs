// P43 T1 - pins the shipping springPop (42 s42.2) before T5 rebuilds the spring around it.
import { test } from "node:test";
import assert from "node:assert/strict";
import { springPop } from "../../scripts/kinetics/spring.mjs";

const params = (Mp) => { const L = Math.log(Mp), z = -L / Math.sqrt(Math.PI * Math.PI + L * L), w = 6 / z; return { z, w, wd: w * Math.sqrt(1 - z * z) }; };

test("springPop lands on exactly 1 and starts at exactly 0", () => {
  assert.equal(springPop(1), 1); assert.equal(springPop(2), 1);
  assert.equal(springPop(0), 0); assert.equal(springPop(-1), 0);
});

test("the inverse model holds: the peak is 1 + Mp at t_p = pi / wd, inside the pop", () => {
  for (const Mp of [0.04, 0.1, 0.2]) {
    const { wd } = params(Mp), tp = Math.PI / wd;
    assert.ok(tp < 1, `t_p ${tp} must land before the pop ends`);
    assert.ok(Math.abs(springPop(tp, Mp) - (1 + Mp)) < 1e-9, `Mp ${Mp}: peak ${springPop(tp, Mp)}`);
    let max = 0; for (let i = 0; i <= 2000; i++) max = Math.max(max, springPop(i / 2000, Mp));
    assert.ok(Math.abs(max - (1 + Mp)) < 1e-4);
  }
});

test("the envelope settles to 0.25% by the end (omega = 6 / zeta), so it lands instead of snapping", () => {
  assert.ok(Math.abs(springPop(0.999) - 1) < 0.004);
  const { z, w } = params(0.04);
  assert.ok(Math.abs(z * w - 6) < 1e-12);
});
