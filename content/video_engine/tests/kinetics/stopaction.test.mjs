// P47 T1 - stop-action: the cadence rule and the frame-index clock, a throw that lands with weight, a landing that sells
// its weight before the drop, the one-frame lag, the tensor's determinant. Every function a pure function of t.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CADENCE, MASS, STOP, cadence, stepped, massParams, lag, throwXf, landXf, stopCss, impactSquash, contactShadow, groundShake, groundDip, rebound, massImpact } from "../../scripts/kinetics/stopaction.mjs";
import { squashMatrix, det2 } from "../../scripts/kinetics/squash.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the cadence rule: on 1s above 154 px/s or for a camera, on 2s below, on 3s for a background boil", () => {
  assert.equal(cadence(300).hold, 1); assert.equal(cadence(154).hold, 2); assert.equal(cadence(40).hold, 2);
  assert.equal(cadence(10, "camera").hold, 1); assert.equal(cadence(10, "boil").hold, 3);
  assert.equal(cadence(300).fps, CADENCE.FPS); assert.equal(cadence(40).fps, CADENCE.FPS / 2); assert.equal(cadence(1, "boil").fps, CADENCE.FPS / 3);
});

test("E99 s30: the on-1s threshold is the cinema-parity reference, 154 px/s (RED 1/7 picture width per second, 1080 stage, 24 fps)", () => {
  assert.equal(CADENCE.ON1_PX_S, 154);
  assert.equal(cadence(200).hold, 1, "200 px/s was on 2s under the old 250; it is on 1s now");
  assert.equal(cadence(150).hold, 2, "150 px/s stays on 2s");
  assert.equal(CADENCE.STROBE_PX_S, 300, "the unread strobe ceiling keeps its value");
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

// ---- P70 T8 (was P69 T69; harvest v2 A35) - THE POOF: a prop appears at its place inside a ring of seeded puffs ------
// Thresholds from the REFERENCE, measured before the module was written (Bravos "The Bubble's Final Phase Has Begun",
// 11:58.0-12:00.3 at 10 fps, docs/research/runs/grill_pipeline-value/bravos-frames/poof.jpg; BRAVOS-RIG-VERIFIED.md:31):
// the cloud's OUTER radius in units of the prop's half-size R, +0.1 .. +0.5 s after the fleck, and its opacity.
import * as SA from "../../scripts/kinetics/stopaction.mjs";

const BRAVOS_REACH = [[0.1, 0.94], [0.2, 1.31], [0.3, 1.66], [0.4, 1.74], [0.5, 1.79]];   // outer radius / R, by pixel difference
const BRAVOS_ALPHA = [[0.4, 0.6], [0.5, 0.25], [0.6, 0.08]];                            // the lobes' opacity
const outer = (p) => Math.max(0, ...p.puffs.map((q) => Math.hypot(q.x, q.y) + q.r));

test("P70 T8: the poof's dials - a 1-2 frame burst, a dispersal of at least 12 frames at 24 fps (W&H p. 74), Bravos's reach", () => {
  const P = SA.POOF;
  assert.ok(P, "stopaction.mjs exports a POOF dial block");
  assert.ok(P.EJECT_S >= 1 / 24 - 1e-9 && P.EJECT_S <= 2 / 24 + 1e-4, "the puffs leave the contact over 1-2 frames");
  assert.ok(P.LIFE_S - P.COVER_S >= 0.5 - 1e-9, "the puff disperses over >= 12 frames at 24 fps (0.5 s)");
  assert.ok(P.COVER_S > P.EJECT_S && P.OPEN_S > P.COVER_S && P.LIFE_S > P.OPEN_S, "burst -> cover -> open -> gone, in that order");
  assert.ok(P.N >= 6 && P.N <= 10, "Bravos's cloud reads as 7-8 lobes");
  assert.equal(P.POP_FROM, 0.6, "the prop springs from 0.6 (the plan's acceptance 1)");
  assert.ok(P.REACH >= 1.5 && P.REACH <= 2.0, "the ring's outer radius at its widest, ~1.8 R with its lobes (Bravos +0.5 s)");
});

test("P70 T8: before its enter a poof draws nothing and the prop is not there", () => {
  const p = SA.poofXf(-0.01);
  assert.equal(p.opacity, 0); assert.equal(p.puffs.length, 0); assert.equal(p.scale, SA.POOF.POP_FROM); assert.equal(p.phase, "waiting");
});

test("P70 T8: the burst - within EJECT_S the cloud already reaches the prop's own size; the contact is EJECT_S", () => {
  const P = SA.POOF;
  assert.ok(outer(SA.poofXf(0)) < 0.2, "a fleck at the contact frame, not a cloud");
  assert.ok(outer(SA.poofXf(P.EJECT_S)) >= 0.75, "two frames later the puffs have ejected over most of the prop (Bravos: 0.94 R by 0.1 s)");
  assert.equal(SA.poofXf(0.3).contact, P.EJECT_S, "the contact the gate, the walk and the cue read");
  assert.equal(SA.poofXf(P.EJECT_S / 2).phase, "burst");
  assert.equal(SA.poofXf((P.EJECT_S + P.COVER_S) / 2).phase, "cover");
  assert.equal(SA.poofXf((P.COVER_S + P.LIFE_S) / 2).phase, "disperse");
  assert.equal(SA.poofXf(P.LIFE_S + 0.01).phase, "settled");
});

test("P70 T8: the puffs eject RADIALLY - each lobe keeps its bearing and only moves outward", () => {
  const ts = Array.from({ length: 40 }, (_, i) => i * SA.POOF.LIFE_S / 40);
  const runs = ts.map((t) => SA.poofXf(t).puffs);
  const n = runs[1].length;
  assert.equal(n, SA.POOF.N);
  for (let i = 0; i < n; i++) {
    const ang = runs.slice(1).map((ps) => Math.atan2(ps[i].y, ps[i].x));
    const dist = runs.slice(1).map((ps) => Math.hypot(ps[i].x, ps[i].y));
    assert.ok(ang.every((a) => near(a, ang[0], 1e-9)), `lobe ${i} keeps its bearing`);
    assert.ok(dist.every((d, k) => k === 0 || d >= dist[k - 1] - 1e-9), `lobe ${i} only moves outward`);
  }
});

test("P70 T8: the cover closes over the prop, then opens into a ring and lets it through (Bravos +0.2 / +0.3)", () => {
  const P = SA.POOF;
  const covers = (p) => p.puffs.some((q) => Math.hypot(q.x, q.y) < q.r);
  assert.ok(covers(SA.poofXf(P.COVER_S)), "at the cover a lobe lies over the prop's centre");
  const hole = (t) => Math.min(...SA.poofXf(t).puffs.map((q) => Math.hypot(q.x, q.y) - q.r));
  assert.ok(hole(P.OPEN_S) > 0.4, "by OPEN_S the lobes have left the prop's heart: a ring, its hole 0.4 R and more");
  assert.ok(hole(P.LIFE_S - 0.01) >= hole(P.OPEN_S) - 1e-9, "... and the hole never closes again");
});

test("P70 T8: the reach and the fade are Bravos's, within a fifth, frame by frame", () => {
  for (const [t, r] of BRAVOS_REACH) {
    const got = outer(SA.poofXf(t));
    assert.ok(Math.abs(got - r) / r <= 0.2, `+${t}s: reach ${got.toFixed(2)} R against Bravos ${r} R`);
  }
  for (const [t, a] of BRAVOS_ALPHA) {
    const got = SA.poofXf(t).puffs[0].alpha;
    assert.ok(Math.abs(got - a) <= 0.15, `+${t}s: alpha ${got.toFixed(2)} against Bravos ~${a}`);
  }
});

test("P70 T8: opaque through the cover, then fading every frame to nothing by LIFE_S", () => {
  const P = SA.POOF;
  assert.ok(SA.poofXf(0).puffs.every((q) => q.alpha === 1) && SA.poofXf(P.COVER_S).puffs.every((q) => q.alpha === 1));
  let prev = 1;
  for (let t = P.COVER_S + 1 / 24; t < P.LIFE_S; t += 1 / 24) {
    const a = SA.poofXf(t).puffs[0].alpha;
    assert.ok(a < prev, `the fade falls at ${t.toFixed(3)}`); prev = a;
  }
  assert.equal(SA.poofXf(P.LIFE_S).puffs.length, 0, "gone at LIFE_S: a puff is never held");
  assert.equal(SA.poofXf(5).puffs.length, 0);
});

test("P70 T8: the prop is absent while the cloud forms, then springs 0.6 -> 1 in front of it and is whole as it opens", () => {
  const P = SA.POOF, end = P.POP_AT + P.POP_S;
  assert.ok(P.POP_AT > P.EJECT_S && P.POP_AT <= P.COVER_S, "it appears once the burst has formed, by the cover (Bravos +0.2)");
  for (const t of [0, P.EJECT_S, P.POP_AT - 0.01]) assert.equal(SA.poofXf(t).opacity, 0, `no prop at +${t.toFixed(3)}s`);
  assert.equal(SA.poofXf(P.POP_AT).scale, P.POP_FROM, "it appears at 0.6 of its size");
  assert.equal(SA.poofXf(P.POP_AT + P.APPEAR_S).opacity, 1, "wholly there two frames later");
  assert.ok(P.APPEAR_S <= 2 / 24 + 1e-4);
  assert.equal(SA.poofXf(end).scale, 1, "the pop lands on exactly 1");
  assert.equal(SA.poofXf(end + 0.4).scale, 1);
  const peak = Math.max(...Array.from({ length: 60 }, (_, i) => SA.poofXf(P.POP_AT + i * P.POP_S / 60).scale));
  assert.ok(peak > 1 && peak <= 1 + (1 - P.POP_FROM) * 0.06, "the pop's small overshoot (Mp 4 %), never a bounce");
  assert.ok(end <= P.OPEN_S + 1e-9, "whole by the time the ring has opened (Bravos +0.3)");
});

test("P70 T8: the opened ring stays a ring - neighbouring lobes still touch round it (their pitch 2 pi d / N)", () => {
  const P = SA.POOF;
  for (const t of [P.OPEN_S, (P.OPEN_S + P.LIFE_S) / 2, P.LIFE_S - 0.02]) {
    const ps = SA.poofXf(t).puffs.map((q) => ({ a: Math.atan2(q.y, q.x), d: Math.hypot(q.x, q.y), r: q.r })).sort((u, v) => u.a - v.a);
    for (let i = 0; i < ps.length; i++) {
      const u = ps[i], v = ps[(i + 1) % ps.length];
      const gap = Math.hypot(u.d * Math.cos(u.a) - v.d * Math.cos(v.a), u.d * Math.sin(u.a) - v.d * Math.sin(v.a)) - u.r - v.r;
      assert.ok(gap <= 0.25, `+${t.toFixed(2)}s: lobes ${i} and ${i + 1} stand ${gap.toFixed(2)} R apart - a ring, not bubbles`);
    }
  }
});

test("P70 T8: seeded, deterministic, a pure function of t - a seek is the play", () => {
  const a = SA.poofXf(0.27, { SEED: 7 }), b = SA.poofXf(0.27, { SEED: 7 }), c = SA.poofXf(0.27, { SEED: 8 });
  assert.deepEqual(a, b);
  SA.poofXf(0.61, { SEED: 7 }); SA.poofXf(0.05, { SEED: 7 });
  assert.deepEqual(SA.poofXf(0.27, { SEED: 7 }), a, "out of order, the same frame");
  assert.notDeepEqual(a.puffs.map((q) => q.x), c.puffs.map((q) => q.x), "another seed is another cloud");
});

test("P70 T8: each lobe carries its shaded underside along the stage light's fall (the drop's LIGHT_DEG)", () => {
  const p = SA.poofXf(0.15), th = (SA.PROP_SHADOW.LIGHT_DEG + 180) * Math.PI / 180;
  for (const q of p.puffs) {
    assert.ok(q.shade, "a shade circle per lobe");
    const dx = q.shade.x - q.x, dy = q.shade.y - q.y;
    assert.ok(near(Math.atan2(dy, dx), Math.atan2(Math.sin(th), Math.cos(th)), 1e-9), "offset down and to the right");
    assert.ok(near(Math.hypot(dx, dy), SA.POOF.SHADE_OFF * q.r, 1e-9));
  }
});
