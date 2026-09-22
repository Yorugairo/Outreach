/* R26-20's other half (E99 s85) - THE STAMP, ported from remotion-ui's badge-stamp. The source is ON DISK at
   content/video_engine/remotion-ui/src/remotion/primitives/badge-stamp.tsx (+ lib/motion-tokens.ts, lib/timing.ts),
   so these are not assertions about a description: every number here is read off the source's own lines, named in
   the assertion. What is pinned is the MECHANISM the intake triaged and the ruling ordered:
     (a) the TWO-SPRING OFFSET - a CLAMPED scale spring landing while a FREE rotation spring is still unwinding, so
         the mark comes to rest slightly OFF-SQUARE (the tell), and at the instant the scale is settled the rotation
         is still measurably off the angle it lands at;
     (b) the IMPACT RING on SPLIT curves - a linear life against an eased expansion to twice the mark's radius,
         which is the fix for the failure the source names, "an impact ring nobody sees";
     (c) the EXIT the landed mark owes (E50) on the source's ease-IN cubic;
     (d) the boundary - the arrival paints nothing and carries nothing, so a card, a badge or a bare prop may each
         be stamped; and the VECTOR MAP's `stamp` species is never touched by any of it. */
import test from "node:test";
import assert from "node:assert/strict";
import {
  STAMP_ARRIVAL, STAMP_LAND, STAMP_TURN, STOP, stampSprings, stampRing, stampExit, stampXf, stopCss, landXf, throwXf,
} from "../../scripts/kinetics/stopaction.mjs";

const near = (a, b, eps, what) => assert.ok(Math.abs(a - b) <= eps, `${what}: ${a} vs ${b} (eps ${eps})`);

test("the dials ARE the source's numbers, each read off its own line", () => {
  assert.equal(STAMP_ARRIVAL.FROM, 2.1);            /* badge-stamp.tsx:88-91 interpolate(land, [0, 1], [2.1, 1], perceptual-scale) */
  assert.equal(STAMP_ARRIVAL.LAND_DEG, -9);         /* :58 rotation */
  assert.equal(STAMP_ARRIVAL.WIND_DEG, 16);         /* :59 windUp */
  assert.deepEqual(STAMP_ARRIVAL.LAND, { m: 0.9, k: 220, c: 14 });   /* :78 damping 14, stiffness 220, mass 0.9, overshootClamping */
  assert.deepEqual(STAMP_ARRIVAL.TURN, { m: 1.0, k: 120, c: 11 });   /* :85 damping 11, stiffness 120, mass 1, free */
  assert.equal(STAMP_ARRIVAL.FADE, 0.35);           /* :93 opacity over land [0, 0.35] */
  assert.deepEqual(STAMP_ARRIVAL.INK, [1, 0.86]);   /* :96 the ink strength off the pressure */
  near(STAMP_ARRIVAL.SHOCK_S, 14 / 30, 1e-12, "the ring's 14 frames at DEFAULT_FPS 30");   /* :106 + timing.ts:3 */
  assert.equal(STAMP_ARRIVAL.RING_TO, 2.0);         /* :156 r * (1 + shock) */
  near(STAMP_ARRIVAL.EXIT_S, 16 / 30, 1e-12, "exitInFrames 16 at DEFAULT_FPS 30");         /* :62 */
});

test("Remotion's spring config IS our mass-spring-damper, in the same two variables", () => {
  /* zeta = c / (2 sqrt(k m)), w0 = sqrt(k / m) - the same conversion massParams does for a material */
  near(STAMP_LAND.z, 14 / (2 * Math.sqrt(220 * 0.9)), 1e-12, "the scale spring's zeta");
  near(STAMP_LAND.w, Math.sqrt(220 / 0.9), 1e-12, "the scale spring's w0");
  near(STAMP_TURN.z, 11 / (2 * Math.sqrt(120 * 1.0)), 1e-12, "the rotation spring's zeta");
  near(STAMP_TURN.w, Math.sqrt(120 / 1.0), 1e-12, "the rotation spring's w0");
  /* both are underdamped at zeta ~ 0.5, and the ROTATION is the slower one - which is why it trails */
  assert.ok(STAMP_LAND.z < 1 && STAMP_TURN.z < 1);
  assert.ok(STAMP_TURN.w < STAMP_LAND.w, "the trailing spring is the slower one");
});

test("(a) THE OFFSET: the scale spring is clamped at 1 while the rotation is still off-axis", () => {
  /* the source clamps the scale's overshoot (:72-74 "an overshoot past 1 dips the settled seal under its own size,
     which reads as a wobble rather than as weight"). The crossing is solved, not watched: */
  near(STAMP_LAND.tc, 0.15417, 5e-5, "the scale lands at tc");
  for (const t of [STAMP_LAND.tc, 0.1667, 0.2083, 0.5, 1.0, 3.0]) {
    assert.equal(stampSprings(t).scale, 1, `the scale is EXACTLY 1 from tc on (t=${t})`);
  }
  /* ... and at that very instant the free spring has not finished: 4.71 deg still to unwind */
  near(stampSprings(STAMP_LAND.tc).off_deg, 4.705, 5e-3, "the offset at the scale's landing");
  /* the golden pair's own instant, 4 frames at 24 fps after the contact */
  const mid = stampXf("ink", 0.1667);
  assert.equal(mid.scale, 1, "the scale has settled");
  near(mid.off_deg, 3.659, 5e-3, "the rotation is still 3.66 deg off its landed angle");
  near(mid.rot, -5.341, 5e-3, "so the mark stands at -5.34 deg, not at its -9 deg landing");
  /* the FREE spring overshoots (the clamped one cannot): the mark turns PAST its landing and comes back */
  const past = [0.25, 0.2917, 0.3333].map((t) => stampSprings(t).off_deg);
  assert.ok(past.every((v) => v < 0), `the rotation overshoots its landing: ${past.map((v) => v.toFixed(3))}`);
  /* and it comes to rest OFF-SQUARE - at its landing angle, which is not zero. A stamp never lands square. */
  const rest = stampXf("ink", 1.30);
  assert.equal(rest.phase, "settled");
  near(rest.rot, STAMP_ARRIVAL.LAND_DEG, 0.02, "the mark rests on its landing angle");
  assert.ok(Math.abs(rest.rot) > 8, "... which is off-square by design");
});

test("(b) THE IMPACT RING on SPLIT curves - linear life, eased expansion to 2x radius", () => {
  assert.equal(stampRing(0), null, "nothing before the contact frame - the shockwave cannot precede its cause");
  assert.equal(stampRing(STAMP_ARRIVAL.SHOCK_S), null, "and nothing once the life is spent");
  assert.equal(stampRing(9.9), null, "an impact ring can never be HELD - which is what keeps it clear of E56's annotation ring");
  /* the LIFE is linear: the alpha and the width fall on a straight line (:159-160) */
  for (const u of [0.25, 0.5, 0.75]) {
    const r = stampRing(u * STAMP_ARRIVAL.SHOCK_S);
    near(r.alpha, STAMP_ARRIVAL.RING_A * (1 - u), 1e-9, `the ring's alpha at life ${u}`);
    near(r.width, STAMP_ARRIVAL.RING_W_PX * (1 - u * STAMP_ARRIVAL.RING_W_FADE), 1e-9, `the ring's width at life ${u}`);
  }
  /* the EXPANSION is NOT linear: eased out (EASING.enter, cubic-bezier(0.16, 1, 0.3, 1)), so it leaves the impact
     fast and decelerates - at half its life it is already 97 % of the way to 2x */
  const half = stampRing(0.5 * STAMP_ARRIVAL.SHOCK_S);
  near(half.r, 1.9718, 5e-4, "the radius at half life");
  assert.ok(half.r > 1 + 0.5 * (STAMP_ARRIVAL.RING_TO - 1) + 0.3, "the expansion is eased, not linear");
  /* it reaches twice the mark's own radius, and never more */
  near(stampRing(0.999 * STAMP_ARRIVAL.SHOCK_S).r, 2.0, 1e-3, "the ring reaches 2x");
  for (let u = 0.001; u < 1; u += 0.01) assert.ok(stampRing(u * STAMP_ARRIVAL.SHOCK_S).r <= 2.0 + 1e-9);
  /* and it is monotone: a ring that came back would read as a pulse, not as an impact */
  let prev = 0;
  for (let u = 0.001; u < 1; u += 0.005) { const r = stampRing(u * STAMP_ARRIVAL.SHOCK_S).r; assert.ok(r >= prev - 1e-12); prev = r; }
});

test("(c) THE EXIT the landed mark owes (E50), on the source's ease-IN cubic", () => {
  assert.equal(stampExit(0), 0);
  assert.equal(stampExit(STAMP_ARRIVAL.EXIT_S), 1);
  assert.equal(stampExit(99), 1, "clamped past its own length");
  for (const u of [0.25, 0.5, 0.75]) near(stampExit(u * STAMP_ARRIVAL.EXIT_S), u ** 3, 1e-9, `ease-IN cubic at ${u}`);
  /* "Never ease-out an exit" (lib/timing.ts:9): it must be SLOWER than linear at the start */
  assert.ok(stampExit(0.5 * STAMP_ARRIVAL.EXIT_S) < 0.5);
});

test("PERCEPTUAL SCALE: the approach is mixed in AREA space, as Remotion's `output: \"perceptual-scale\"` is", () => {
  /* remotion/dist/cjs/interpolate.js:272-283, :327-330 (4.0.502): toSignedArea(s) = s^2, mix, sqrt */
  const at = (land) => Math.sqrt(2.1 * 2.1 + (1 - 2.1 * 2.1) * land);
  for (const t of [0.01, 0.03, 0.06, 0.1, 0.14]) {
    const sp = stampSprings(t);
    near(sp.scale, at(sp.land), 1e-12, `the scale at land ${sp.land.toFixed(3)}`);
  }
  /* the two ends are the source's, and the middle is NOT the linear mix */
  assert.equal(stampSprings(0).scale, 2.1);
  assert.equal(stampSprings(1.0).scale, 1);
  near(at(0.5), 1.6447, 1e-4, "land 0.5 in area space");
  assert.ok(at(0.5) - (2.1 + (1 - 2.1) * 0.5) > 0.09, "and the linear 1.55 is 0.095 below it");
});

test("the arrival is pure in t, and a seek IS the play", () => {
  for (const t of [0, 0.05, 0.1667, 0.4, 1.3, 9.0]) {
    const a = stampXf("ink", t), b = stampXf("ink", t);
    assert.deepEqual(a, b, `t=${t} is the same state twice`);
    for (const k of ["x", "y", "rot", "scale", "off_deg", "ink", "opacity", "alpha", "h", "ground"]) {
      assert.ok(Number.isFinite(a[k]), `t=${t}: ${k} is a finite number (deepEqual passes NaN against NaN): ${a[k]}`);
    }
  }
  const before = stampXf("ink", -0.1);
  assert.equal(before.phase, "waiting");
  assert.equal(before.opacity, 0, "nothing is on the page before the contact");
  assert.equal(before.scale, STAMP_ARRIVAL.FROM, "... and it waits oversized, where it is thrown from");
  assert.equal(before.ring, null);
});

test("the RECEIVER answers in this module's own vocabulary - and the mark never hops", () => {
  /* the page dips by the material's spring and recovers; a stamp does not fall, so there is no rebound */
  const ys = [0.02, 0.06, 0.12, 0.4, 1.2].map((t) => stampXf("ink", t).ground);
  assert.ok(ys[0] > 0 && ys[0] > ys[4], `the surface dips at the contact and recovers: ${ys.map((v) => v.toFixed(3))}`);
  assert.ok(Math.max(...ys) < 5, "a dip, never a stage shake (the report Q3)");
  /* metal hits harder than paper - the same law every landing obeys */
  assert.ok(stampXf("metal", 0.05).ground > stampXf("paper", 0.05).ground);
});

test("the CONTACT SHADOW's height tracks the approach: far while the mark is still coming down, 0 once it is on the page", () => {
  /* R26-20 review H2: h read a dial that is not on STAMP_ARRIVAL and was NaN on every call */
  const hs = [-0.1, 0, 0.02, 0.05, 0.08, 0.12, STAMP_LAND.tc, 0.3, 1.3].map((t) => stampXf("ink", t).h);
  for (const h of hs) assert.ok(Number.isFinite(h), `h is finite: ${hs}`);
  near(hs[0], STOP.SHADOW_H_PX, 1e-9, "before the contact the mark is at its full oversize: the shadow is at its far height");
  near(hs[1], STOP.SHADOW_H_PX, 1e-9, "... and at the contact frame itself");
  for (let i = 2; i < hs.length; i++) assert.ok(hs[i] <= hs[i - 1] + 1e-9, `and it falls as the mark comes down: ${hs.map((v) => v.toFixed(2))}`);
  assert.ok(hs[3] > 0 && hs[3] < STOP.SHADOW_H_PX, "mid-approach it is in between");
  assert.equal(hs[6], 0, "and it is 0 from the instant the scale lands");
  assert.equal(stampXf("ink", 0.05, { SHADOW_H_PX: 80 }).h * 2, stampXf("ink", 0.05).h, "an override reaches it, as every STOP dial can be");
});

test("(d) the arrival carries NOTHING - it is a motion, and it paints nothing", () => {
  const st = stampXf("ink", 0.2);
  assert.deepEqual(Object.keys(st).sort(), ["alpha", "ground", "h", "ink", "off_deg", "opacity", "phase",
                                            "ring", "rot", "scale", "shake", "theta", "u", "x", "y"].sort(),
                   "a pose and nothing else: no payload, no colour, no geometry of a card");
});

test("stopCss writes the stamp's scale, and writes NOTHING new for every other arrival", () => {
  assert.match(stopCss(stampXf("ink", 0.05)), /scale\(/, "a stamp's pose carries its scale");
  /* the byte-identity that keeps every committed golden: a throw's and a landing's CSS is what it was */
  for (const t of [0, 0.1, 0.3, 0.6, 1.5]) {
    assert.ok(!stopCss(landXf("paper", t)).includes("scale("), `a landing's CSS at t=${t} carries no scale`);
    assert.ok(!stopCss(throwXf({ x: 300, y: -200 }, "paper", t)).includes("scale("), `a throw's CSS at t=${t} carries no scale`);
  }
  /* ... and a state whose scale IS 1 writes none either */
  assert.ok(!stopCss({ x: 0, y: 0, scale: 1 }).includes("scale("));
});
