// P47 T1 - stop-action: the cadence rule and the frame-index clock, a throw that lands with weight, a landing that sells
// its weight before the drop, the one-frame lag, the tensor's determinant. Every function a pure function of t.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CADENCE, MASS, STOP, cadence, stepped, massParams, lag, throwXf, landXf, stopCss, impactSquash, contactShadow, groundShake, groundDip, rebound, massImpact } from "../../scripts/kinetics/stopaction.mjs";
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

test("throw: starts at the offset, flies a ballistic chord on a stepped clock, arrives at speed, lands on the spot and rides the dip", () => {
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
  /* Q4: no deceleration into the contact - the last tenth of the flight covers a tenth of the chord */
  const late = throwXf(from, "paper", 0.9 * F), end = throwXf(from, "paper", F - 1e-9);
  assert.ok(Math.abs((end.x - late.x) - 0.1 * -from.x) < 2, "arrives at speed, never eases into the hit");
  const land = throwXf(from, "paper", F + 1 / 24 + 1e-6);
  assert.equal(land.phase, "land"); assert.equal(land.x, 0);
  assert.ok(land.alpha > 0, "a card squashes on its one squash frame");
  const chord = Math.hypot(from.x, from.y), hop = rebound(1 / 24 + 1e-6, "paper", -from.y + STOP.ARC * chord);
  assert.ok(land.ground > 0 && near(land.y, land.ground + hop, 1e-9), "it rides the ground's dip and its own small hop");
  const rest = throwXf(from, "paper", F + STOP.SETTLE_S + 0.1);
  assert.equal(rest.phase, "settled"); assert.ok(Math.abs(rest.y) < 0.2 && rest.alpha === 0, "at rest on the spot");
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

test("land: weight before motion - the lift and the clamp precede the drop, the drop eases in, the contact is one frame, then the material", () => {
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
  const hit = STOP.ANTIC_S + STOP.DROP_S;
  assert.equal(landXf("metal", hit + 1 / 24 + 1e-6).alpha, 0, "a rigid heavy thing does not squash (Williams p. 263)");
  assert.ok(landXf("paper", hit + 1 / 24 + 1e-6).alpha > 0.05 && landXf("paper", hit + 2 / 24 + 1e-6).alpha === 0, "a card squashes on one frame and releases at once");
  assert.equal(landXf("paper", hit + 1e-6).alpha, 0, "the contact frame itself is uncompressed (Williams pp. 93-94)");
  const rest = landXf("metal", hit + STOP.SETTLE_S + 0.1);
  assert.equal(rest.phase, "settled"); assert.ok(Math.abs(rest.y) < 0.05);
  /* the receiver: metal dips the ground harder and recovers dead; paper's ground flutters back */
  assert.ok(groundDip(0, "metal") > groundDip(0, "paper") && groundDip(0, "metal") <= 6 + 1e-9);
  let metalMin = 0, paperMin = 0;
  for (let i = 0; i <= 100; i++) { metalMin = Math.min(metalMin, groundDip(i * 0.01, "metal")); paperMin = Math.min(paperMin, groundDip(i * 0.01, "paper")); }
  assert.ok(metalMin > -0.15, "dense: critically damped, no overshoot (Q4)");
  assert.ok(paperMin < -0.1, "light: the ground flutters past rest (zeta 0.67 overshoots 5.8 %)");
  assert.ok(groundDip(8 / 24, "metal") < 0.15 * groundDip(0, "metal"), "the dip settles within 4-8 frames");
  /* restitution: a card hops a little, a heavy rigid thing not at all */
  assert.equal(rebound(0.02, "metal", 48), 0);
  let hop = 0; for (let i = 0; i <= 60; i++) hop = Math.min(hop, rebound(i * 0.005, "paper", 160));
  assert.ok(hop < 0 && hop > -0.15 * 0.15 * 160 - 1e-9, "h1 = e^2 h0");
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

test("the hit (Q1): one squash frame for a deformable thing, none for a rigid one, the contact frame uncompressed, on 2s the frame holds two", () => {
  assert.equal(impactSquash(-0.01, "paper"), 0);
  assert.equal(impactSquash(0, "paper"), 0, "frame 0 is the contact drawing");
  assert.ok(near(impactSquash(1 / 24, "paper"), STOP.IMPACT_SQUASH, 1e-12), "frame 1 is the squash");
  assert.equal(impactSquash(2 / 24, "paper"), 0, "released at once - never a hold");
  for (let f = 0; f < 6; f++) assert.equal(impactSquash(f / 24, "metal"), 0, "a rigid thing never squashes");
  assert.ok(impactSquash(1 / 24, "liquid") > 0 && impactSquash(2 / 24, "liquid") > 0 && impactSquash(3 / 24, "liquid") === 0, "a liquid spreads over two");
  assert.ok(near(impactSquash(3 / 24, "paper", 2), STOP.IMPACT_SQUASH, 1e-12), "on 2s the squash frame holds frames 2 and 3");
});

test("the contact shadow comes in: wide and soft while high, a slit on the floor - the blur is the depth (Kersten 1997), the alpha stays narrow", () => {
  const far = contactShadow(STOP.SHADOW_H_PX), near0 = contactShadow(0), mid = contactShadow(STOP.SHADOW_H_PX / 2);
  assert.ok(far.blur > mid.blur && mid.blur > near0.blur && near(far.blur, 16) && near(near0.blur, 0.8), "sigma 16 px high -> 0.8 px at contact");
  assert.ok(far.alpha < mid.alpha && mid.alpha < near0.alpha && near0.alpha - far.alpha <= 0.35, "the alpha ramp is the weakest cue and stays narrow");
  assert.ok(far.scale < mid.scale && mid.scale < near0.scale, "grows as it nears the floor");
  assert.ok(near(near0.alpha, STOP.SHADOW_NEAR.alpha) && near(far.alpha, STOP.SHADOW_FAR.alpha));
  assert.ok(contactShadow(0, 0.2).scale > near0.scale, "the hit's squash spreads the shadow");
  assert.equal(contactShadow(1e9).alpha, STOP.SHADOW_FAR.alpha, "clamped high");
});

test("the ground answers with a DIP for mass; the shake is violence and only a violent hit gets it", () => {
  const f0 = groundShake(0, "metal"), f1 = groundShake(1 / 24 + 1e-4, "metal"), f3 = groundShake(3 / 24 + 1e-4, "metal");
  assert.ok(f0.x !== 0 && f1.x !== 0 && f0.x * f1.x < 0, "the shake alternates sides");
  assert.deepEqual(f3, { x: 0, y: 0 }, "and is gone by the fourth frame");
  assert.deepEqual(groundShake(-0.1, "metal"), { x: 0, y: 0 });
  const hit = STOP.ANTIC_S + STOP.DROP_S + 1e-6;
  assert.deepEqual(landXf("metal", hit).shake, { x: 0, y: 0 }, "no shake by default - mass is the dip");
  assert.ok(landXf("metal", hit).ground > 0 && throwXf({ x: -400, y: -120 }, "paper", STOP.FLIGHT_S + 1e-6).ground > 0, "both arrivals dip the ground on the hit");
  assert.ok(landXf("metal", hit, { violent: true }).shake.x !== 0, "a violent hit shakes the stage");
  assert.ok(throwXf({ x: -400, y: -120 }, "paper", 0.1).h > 0 && landXf("metal", 0.05).h > STOP.DROP_PX, "the height above rest is reported for the shadow");
});
