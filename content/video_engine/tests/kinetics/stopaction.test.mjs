// P47 T1 - stop-action: the cadence rule and the frame-index clock, a throw that lands with weight, a landing that sells
// its weight before the drop, the one-frame lag, the tensor's determinant. Every function a pure function of t.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CADENCE, MASS, STOP, cadence, stepped, massParams, lag, throwXf, landXf, stopCss } from "../../scripts/kinetics/stopaction.mjs";
import { squashMatrix, det2 } from "../../scripts/kinetics/squash.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the cadence rule: on 1s above 250 px/s or for a camera, on 2s below, on 3s for a background boil", () => {
  assert.equal(cadence(300).hold, 1); assert.equal(cadence(250).hold, 2); assert.equal(cadence(40).hold, 2);
  assert.equal(cadence(10, "camera").hold, 1); assert.equal(cadence(10, "boil").hold, 3);
  assert.equal(cadence(300).fps, CADENCE.FPS); assert.equal(cadence(40).fps, CADENCE.FPS / 2); assert.equal(cadence(1, "boil").fps, CADENCE.FPS / 3);
  assert.equal(CADENCE.ON1_PX_S, 250);
});

test("the stepped clock quantises on the INTEGER frame index: round(t * fps) then floor(frame / hold)", () => {
  assert.equal(stepped(1.2345, 1), 1.2345, "on 1s the clock is the clock");
  // 24 fps, on 2s: frames 0..23 -> steps at even frames
  for (let f = 0; f < 48; f++) { const t = f / 24; assert.ok(near(stepped(t, 2, 24), Math.floor(f / 2) * 2 / 24), `frame ${f}`); }
  // the renderer's seek t = frame / fps can sit a ulp under the boundary: round() lands it on the frame, floor(t * fps) would not
  const t = 7 / 24;   // frame 7 exactly (as a double it is 0.29166666..., and 7/24 * 24 is not always 7)
  assert.ok(near(stepped(t, 2, 24), 6 / 24), "frame 7 belongs to step 3 (frames 6-7)");
  assert.ok(near(stepped(t + 1e-12, 2, 24), 6 / 24) && near(stepped(t - 1e-12, 2, 24), 6 / 24), "a ulp either side of the frame is the same frame");
});

test("materials: the presets' zeta and w0 from m, k, c; an unknown name is paper", () => {
  const p = massParams("paper"); assert.ok(near(p.z, 18 / (2 * Math.sqrt(180)), 1e-12) && near(p.w, Math.sqrt(180), 1e-12));
  assert.ok(massParams("liquid").z > 1, "capital flow is overdamped");
  assert.ok(Math.abs(massParams("ink").z - 1) < 0.03, "ink on paper is critically damped");
  assert.equal(massParams("granite").name, "paper");
  assert.deepEqual(Object.keys(MASS), ["paper", "metal", "liquid", "ink"]);
});

test("lag: what a thing drags reads the clock one frame late", () => {
  assert.ok(near(lag(1.0), 1.0 - 1 / 24)); assert.ok(near(lag(1.0, 2, 30), 1.0 - 2 / 30));
  assert.equal(STOP.LAG_FRAMES, 1);
});

test("throw: starts at the offset, flies on a stepped clock, lands on the spot with an impact and settles to rest", () => {
  const from = { x: -400, y: -120 }, F = STOP.FLIGHT_S;
  const s0 = throwXf(from, "paper", 0);
  assert.equal(s0.x, from.x); assert.equal(s0.y, from.y); assert.equal(s0.phase, "flight");
  assert.equal(s0.hold, 1, "417 px in 0.45 s is 927 px/s: on 1s");
  let above = 0, prevX = from.x;
  for (let i = 1; i < 24; i++) {
    const s = throwXf(from, "paper", (i / 24) * F);
    assert.ok(s.x >= prevX - 1e-9, "the chord is covered monotonically"); prevX = s.x;
    const chordY = from.y * (1 - (s.x - from.x) / -from.x);
    if (s.y < chordY - 1) above++;
  }
  assert.ok(above > 12, "the arc lifts above the chord for most of the flight");
  const land = throwXf(from, "paper", F + 1e-6);
  assert.equal(land.phase, "land"); assert.equal(land.x, 0);
  assert.ok(land.alpha > 0, "the impact squashes");
  let maxSink = 0;
  for (let i = 0; i <= 60; i++) { const s = throwXf(from, "paper", F + i * 0.02); maxSink = Math.max(maxSink, s.y); }
  assert.ok(maxSink > 0 && maxSink <= STOP.IMPACT_PX + 1e-9, "it sinks, never more than IMPACT_PX");
  const rest = throwXf(from, "paper", F + STOP.SETTLE_S + 0.1);
  assert.equal(rest.phase, "settled"); assert.ok(Math.abs(rest.y) < 0.2 && rest.alpha < 0.002, "at rest on the spot");
  assert.deepEqual(throwXf(from, "paper", 1.0), throwXf(from, "paper", 1.0), "pure");
  const slow = throwXf({ x: -60, y: 0 }, "paper", 0);
  assert.equal(slow.hold, 2, "60 px in 0.45 s is 133 px/s: on 2s");
});

test("throw: the stepped flight holds its pose inside a frame pair on 2s", () => {
  const from = { x: -60, y: 0 };
  const a = throwXf(from, "paper", 2 / 24 + 0.001), b = throwXf(from, "paper", 3 / 24 - 0.001);
  assert.equal(a.x, b.x, "frames 2 and 3 share a pose on 2s");
  const c = throwXf(from, "paper", 4 / 24 + 0.001);
  assert.notEqual(a.x, c.x, "frame 4 is the next step");
});

test("land: weight before motion - the lift and the clamp precede the drop, the drop eases in, the impact settles by the material", () => {
  const w = landXf("metal", -0.1);
  assert.equal(w.phase, "waiting"); assert.equal(w.y, -STOP.DROP_PX);
  const a = landXf("metal", STOP.ANTIC_S / 2);
  assert.equal(a.phase, "anticipation");
  assert.ok(a.y < -STOP.DROP_PX, "it LIFTS before it drops");
  assert.ok(a.alpha < 0, "the clamp compresses before anything moves");
  const d1 = landXf("metal", STOP.ANTIC_S + STOP.DROP_S * 0.3), d2 = landXf("metal", STOP.ANTIC_S + STOP.DROP_S * 0.9);
  assert.equal(d1.phase, "drop");
  assert.ok((d1.y + STOP.DROP_PX) < 0.1 * STOP.DROP_PX, "easing IN: little travel early");
  assert.ok(d2.y > d1.y && d2.alpha > d1.alpha, "fast and stretching late");
  const im = landXf("metal", STOP.ANTIC_S + STOP.DROP_S + 1e-6);
  assert.equal(im.phase, "land"); assert.ok(im.alpha > 0.05, "the impact squash");
  const rest = landXf("metal", STOP.ANTIC_S + STOP.DROP_S + STOP.SETTLE_S + 0.1);
  assert.equal(rest.phase, "settled"); assert.ok(Math.abs(rest.y) < 0.05);
  // the materials differ in their settle: paper overshoots, liquid never does
  let paperMin = 0, liquidMin = 0;
  for (let i = 0; i <= 100; i++) { const ts = STOP.ANTIC_S + STOP.DROP_S + i * 0.01; paperMin = Math.min(paperMin, landXf("paper", ts).y); liquidMin = Math.min(liquidMin, landXf("liquid", ts).y); }
  assert.ok(paperMin < -0.3, "paper springs back past rest (overshoot)");
  assert.ok(liquidMin > -1e-9, "liquid never overshoots");
});

test("the tensor keeps det = 1 in every phase, and stopCss writes fixed decimals", () => {
  for (const t of [0.1, 0.3, 0.46, 0.6, 1.0]) {
    const s = throwXf({ x: -300, y: -80 }, "paper", t), a = Math.abs(s.alpha);
    assert.ok(near(det2(squashMatrix(s.theta, a)), 1, 1e-9), `det at ${t}`);
  }
  const css = stopCss(throwXf({ x: -300, y: -80 }, "paper", 0.2));
  assert.match(css, /^ translate\(-?\d+\.\d{2}px,-?\d+\.\d{2}px\) rotate\(-?\d+\.\d{2}deg\)( matrix\([-\d.,]+,0,0\))?$/);
  assert.equal(stopCss({ x: 0, y: 0, alpha: 0 }), " translate(0.00px,0.00px)");
  const clamp = stopCss({ x: 0, y: 0, alpha: -0.05, theta: Math.PI / 2 });
  assert.match(clamp, /matrix\(/, "a clamp goes through the tensor with the axis turned");
});
