// P72 T46e (R26-368 (b)): the cadence rule in PICTURE WIDTHS per second - E99 s30's own definition. 154 px/s is RED's
// pan rule, 1/7 picture width per second, stated on the 1080 stage; on H's 1920 stage the same rule is 274 px/s.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CADENCE, cadence, throwXf } from "../../scripts/kinetics/stopaction.mjs";

test("the rule is a share of the picture's width: 154 px/s on the 1080 stage is 1/7 of it per second", () => {
  assert.equal(CADENCE.STAGE_W_REF, 1080, "the stage E99 s30 stated 154 on");
  assert.ok(Math.abs(CADENCE.ON1_PW_S - 1 / 7) < 0.001, `ON1_PW_S ${CADENCE.ON1_PW_S} is 1/7 picture width per second`);
  assert.equal(CADENCE.ON1_PW_S * CADENCE.STAGE_W_REF, CADENCE.ON1_PX_S, "the pixel figure is the rule on its own stage");
});

test("the same speed steps differently on a wider picture: 200 px/s is on 1s at 1080, on 2s at 1920", () => {
  assert.equal(cadence(200).hold, 1, "no stage named: the 1080 stage the rule was stated on");
  assert.equal(cadence(200, "translate", { stage_w: 1080 }).hold, 1);
  assert.equal(cadence(200, "translate", { stage_w: 1920 }).hold, 2, "200 px/s is 0.104 of 1920 per second, under 1/7");
  assert.equal(cadence(280, "translate", { stage_w: 1920 }).hold, 1, "280 px/s clears 274 on the 1920 stage");
  assert.equal(cadence(273, "translate", { stage_w: 1920 }).hold, 2, "the 1920 stage's threshold is 154 x 1920 / 1080 = 273.8");
  assert.equal(cadence(274, "translate", { stage_w: 1920 }).hold, 1);
});

test("the why names the threshold on the stage it was read on; the 1080 wording is unchanged", () => {
  assert.equal(cadence(359).why, "359 px/s > 154: on 1s");
  assert.equal(cadence(200, "translate", { stage_w: 1920 }).why, "200 px/s <= 274 (1/7 of the 1920 stage): on 2s");
  assert.equal(cadence(10, "camera", { stage_w: 1920 }).hold, 1, "a camera move still steps every frame");
  assert.equal(cadence(10, "boil", { stage_w: 1920 }).hold, 3, "a boil still steps on 3s");
});

test("a throw reads its cadence on the stage its caller names", () => {
  const from = { x: 0, y: -90 };   // 90 px over 0.45 s = 200 px/s
  assert.equal(throwXf(from, "paper", 0.1).hold, 1, "no stage: the 1080 rule, 200 > 154");
  assert.equal(throwXf(from, "paper", 0.1, { stage_w: 1920 }).hold, 2, "on the 1920 stage 200 <= 274: on 2s");
});
