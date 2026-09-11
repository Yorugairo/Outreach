// P50 T10 + T13 - THE BREAKTHROUGH's FURNITURE and its STOP-MOTION cadence (E60; R26-30). The module is math
// only - lpPaintBreakthrough owns the DOM - so these tests pin the placeholder's clock, the track's height, the
// axis capsule and its leader, the cadence the burst's own speed asks for, and the two properties the blend is
// accepted on: the stepped run is piecewise constant and monotone, and it rests on the continuous burst's frame.
import { test } from "node:test";
import assert from "node:assert/strict";
import { BREAK, breakPlaceholder, breakTrack, breakStamp, breakCapsule, breakCapsuleFit, breakLeader, breakLeaderX,
  burstSpeed, burstCadence, breakStep, burstClock } from "../../scripts/species/breakthrough.mjs";
import { stepped, CADENCE } from "../../scripts/kinetics/stopaction.mjs";

// the Tokyo breakthrough page, the one the ruling was made on: bonds 1.52 % against chips 36.59 %, the scale
// stated to 8 % and rewritten to 40 %, over a portrait plot of ~780 viewBox units, BT_RUN 0.6 s
// MEASURED off the built page (portrait, 2026-09-11): plot 297 viewBox units, base 447, the chart's box 517 tall
const TOKYO = { plot: 297, lo: 0, hi0: 8, hi1: 40, comp: 1.52, v: 36.59, run_s: 0.6, settle_s: 0.3, base: 447, chartH: 517 };
const PILL_P = { w: 160, h: 84, ty: 61, up: 128, dn: 40, rx: 14 };   // the builder's portrait callout pill
const PILL_L = { w: 128, h: 42, ty: 30, up: 66, dn: 24, rx: 8 };     // ... and its landscape one
const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the dials are the burst's furniture, and the track never reads as a second bar", () => {
  assert.equal(BREAK.PH_TEXT, "?");
  assert.ok(BREAK.PH_ALPHA > 0 && BREAK.PH_ALPHA < 0.35, "furniture, not data (E28)");
  assert.ok(BREAK.PH_OUT_S > 0 && BREAK.PH_OUT_S < 0.5, "gone before the shoot - shorter than BT_HOLD (0.5 s)");
  assert.ok(BREAK.CAP_PAD > 0 && BREAK.CAP_LEAD_GAP > 0 && BREAK.CAP_LEAD_DX > 0 && BREAK.CAP_LAB_UP > 0);
  assert.ok(BREAK.CAP_MIN_H > 0 && BREAK.CAP_FLOOR > 0);
  assert.match(BREAK.CAP_LEAD_DASH, /\d+\s+\d+/, "the leader is DOTTED: a solid rule is a comparator (E53 s6)");
  assert.equal(BREAK.STEP_FPS, CADENCE.FPS, "the stop clock is stopaction's own");
});

// ---------------------------------------------------------------- the placeholder
test("the '?' stands through the BUILD and leaves the moment the number is spoken", () => {
  for (const secs of [-3, -1.2, -0.4, -1e-6]) {
    const p = breakPlaceholder(secs);
    assert.equal(p.on, true, `secs ${secs}: the number is not spoken yet`);
    assert.equal(p.k, 1);
    assert.equal(p.text, "?");
  }
  assert.equal(breakPlaceholder(0).on, false, "secs 0 IS the start of the hold: the number is spoken");
  assert.equal(breakPlaceholder(0.3).on, false);
});

test("the track fades out over PH_OUT_S of the hold, monotonically, and never comes back", () => {
  assert.equal(breakPlaceholder(-1).alpha, BREAK.PH_ALPHA);
  assert.ok(near(breakPlaceholder(BREAK.PH_OUT_S / 2).alpha, BREAK.PH_ALPHA / 2, 1e-9));
  assert.equal(breakPlaceholder(BREAK.PH_OUT_S).alpha, 0);
  assert.equal(breakPlaceholder(10).alpha, 0);
  let prev = Infinity;
  for (let s = -0.5; s <= 1.0; s += 0.01) { const a = breakPlaceholder(s).alpha; assert.ok(a <= prev + 1e-12); prev = a; }
});

test("the track is the COMPARATOR's height at the bar's own x - never the breaking value's", () => {
  const base = 900, yComp = 760;                       // the comparator's level on the stated scale
  const T = breakTrack(120, 60, base, yComp);
  assert.deepEqual([T.x, T.w], [120, 60], "the bar's own column");
  assert.equal(T.y, yComp);
  assert.equal(T.h, base - yComp, "exactly the height the bar builds to: no scale the page did not state");
  assert.equal(breakTrack(0, 10, 900, 899.5).h, 3, "a comparator at zero still leaves a visible slot");
});

test("the MARK stands where the number will - over the track's top edge, at the value label's own offset", () => {
  const T = breakTrack(120, 60, 900, 760);
  const S = breakStamp(T, 14);
  assert.equal(S.x, 150, "centred on the bar's column");
  assert.equal(S.y, 760 - 14, "the value label's place: the track alone is covered by the bar that grows into it");
});

// ---------------------------------------------------------------- the axis capsule
test("the capsule mounts ON THE AXIS and the bar's own name goes ABOVE the zero line", () => {
  const base = 440, capH = 42;
  const C = breakCapsule(base, capH);
  assert.equal(C.y, base + BREAK.CAP_PAD, "under the zero baseline by the pad");
  assert.ok(C.labY < base, "the capsule TAKES the x-label's row, so the name is written inside the bar's foot");
  assert.equal(C.labY, base - BREAK.CAP_LAB_UP);
});

test("the axis mount FITS ITS BAND - the measured portrait page had 70 units for an 84-unit pill", () => {
  const F = breakCapsuleFit(TOKYO.base, TOKYO.chartH, PILL_P);
  assert.equal(F.y, TOKYO.base + BREAK.CAP_PAD);
  assert.ok(F.y + F.h <= TOKYO.chartH - BREAK.CAP_FLOOR + 1e-9,
    `the capsule (${F.y}-${F.y + F.h}) must stay inside the chart's box (${TOKYO.chartH}): the citation is below it (E52)`);
  assert.ok(F.h < PILL_P.h && F.h >= BREAK.CAP_MIN_H, `shrunk to ${F.h}, never under the floor`);
  assert.ok(Math.abs(F.ty / PILL_P.ty - F.k) < 1e-12, "the baseline inside the box shrinks with it ...");
  assert.ok(F.k > 0 && F.k < 1, "... and so does the type, by the same factor");
});

test("a LANDSCAPE page has room and the fit changes nothing", () => {
  const F = breakCapsuleFit(440, 560, PILL_L);
  assert.equal(F.h, PILL_L.h);
  assert.equal(F.k, 1);
  assert.equal(F.ty, PILL_L.ty);
});

test("the fit never shrinks a capsule below the readable floor, however thin the band", () => {
  const F = breakCapsuleFit(440, 450, PILL_P);   // a page with almost nothing under its axis
  assert.equal(F.h, BREAK.CAP_MIN_H, "a capsule that cannot be read is not a capsule - the page is refused by the eye, not silently ruined");
});

test("the leader is routed CLEAR of the bar - a vertical bar's end is above the capsule, so a line between them crosses it", () => {
  const x0 = 60, bx = 300, bw = 90;
  assert.equal(breakLeaderX(bx, bw, x0), bx - BREAK.CAP_LEAD_DX, "outside the near edge ...");
  assert.ok(breakLeaderX(bx, bw, x0) > x0, "... and inside the plot");
  assert.equal(breakLeaderX(x0 + 2, bw, x0), x0 + 2 + bw + BREAK.CAP_LEAD_DX, "a bar against the axis routes on its far side");
});

test("the dotted leader runs from the bar's END down to the capsule, and is nothing when there is no room", () => {
  const base = 440, C = breakCapsule(base, 42);
  const L = breakLeader(300, 120, C.y);                 // a bar whose tip is high on the page
  assert.equal(L.x, 300);
  assert.equal(L.y1, 120 + BREAK.CAP_LEAD_GAP, "it starts clear of the tip");
  assert.equal(L.y2, C.y - BREAK.CAP_LEAD_GAP, "and stops clear of the capsule");
  assert.ok(L.y2 > L.y1);
  assert.equal(breakLeader(300, C.y - 2, C.y), null, "a tip that has not cleared the capsule points at itself");
});

// ---------------------------------------------------------------- the cadence
test("the burst's own speed is the TIP's travel over the run, and the rule puts it on 1s", () => {
  const v = burstSpeed(TOKYO.plot, TOKYO.lo, TOKYO.hi0, TOKYO.hi1, TOKYO.comp, TOKYO.v, TOKYO.run_s);
  const want = TOKYO.plot * (TOKYO.v / TOKYO.hi1 - TOKYO.comp / TOKYO.hi0) / TOKYO.run_s;
  assert.ok(near(v, want, 1e-9), `${v} vs ${want}`);
  assert.ok(v > CADENCE.ON1_PX_S, "the shoot is far faster than the on-1s threshold");
  const cad = burstCadence(TOKYO.plot, TOKYO.lo, TOKYO.hi0, TOKYO.hi1, TOKYO.comp, TOKYO.v, TOKYO.run_s);
  assert.equal(cad.hold, 1, "on 1s: a bar crossing ~940 units/s strobes on anything slower");
  assert.equal(cad.fps, CADENCE.FPS);
  // ... and THAT is why the cadence is read on the page's own units: the same page halved (a park) would fall
  // to on-2s, so a parked burst would step differently from the one the page was designed on
  assert.equal(burstCadence(TOKYO.plot / 2, TOKYO.lo, TOKYO.hi0, TOKYO.hi1, TOKYO.comp, TOKYO.v, TOKYO.run_s).hold, 2);
  // a slow crawl of a burst would step on 2s - the rule is the module's, not a constant here
  assert.equal(burstCadence(40, TOKYO.lo, TOKYO.hi0, TOKYO.hi1, TOKYO.comp, TOKYO.v, TOKYO.run_s).hold, 2);
});

test("breakStep quantises on the frame index at hold 1, where stopaction's `stepped` returns t unchanged", () => {
  assert.equal(stepped(0.401, 1, 24), 0.401, "stopaction assumes the renderer IS on 1s");
  assert.ok(near(breakStep(0.401, 1, 24), 10 / 24, 1e-12), "ours does not: render_episode.py runs at 30 fps");
  for (const [t, hold] of [[0.37, 2], [0.51, 2], [0.9, 3], [1.4, 2]])
    assert.equal(breakStep(t, hold, 24), stepped(t, hold, 24), "and for hold > 1 it IS stopaction's formula");
  assert.equal(breakStep(-1), 0);
  assert.equal(breakStep(0), 0);
});

// ---------------------------------------------------------------- the run's clock
const cont = (run) => burstClock(run, TOKYO.run_s, TOKYO.settle_s, null);

test("with no cadence the clock is EXACTLY the continuous burst's two clamps - the option off changes nothing", () => {
  const c01 = (v) => Math.min(1, Math.max(0, v));
  for (let run = -0.4; run <= 1.4; run += 0.017) {
    const K = cont(run);
    assert.equal(K.t, run);
    assert.ok(near(K.u1, c01(run / TOKYO.run_s), 1e-12));
    assert.ok(near(K.u2, c01((run - TOKYO.run_s) / TOKYO.settle_s), 1e-12));
    assert.equal(K.landed, false, "the continuous glow law stays with its caller");
    assert.equal(K.step, -1);
  }
});

const stop = (run, cad = { hold: 1, fps: 24 }) => burstClock(run, TOKYO.run_s, TOKYO.settle_s, cad);

test("the stepped shoot is PIECEWISE CONSTANT between frames and monotone across them", () => {
  const fps = 24;
  for (let f = 0; f < 20; f++) {                         // inside one frame nothing moves
    const t0 = f / fps + 1e-4, t1 = (f + 0.49) / fps;
    assert.equal(stop(t0).u1, stop(t1).u1, `frame ${f} holds`);
    assert.equal(stop(t0).t, stop(t1).t);
  }
  let prev = -1;
  for (let run = 0; run <= 1.2; run += 1 / 240) {        // and never goes backwards
    const u = stop(run).u1;
    assert.ok(u >= prev - 1e-12, `u1 fell at run ${run}`);
    prev = u;
  }
  const seen = new Set();
  for (let run = 0; run < TOKYO.run_s; run += 1 / 480) seen.add(stop(run).u1.toFixed(9));
  assert.ok(seen.size <= Math.ceil(TOKYO.run_s * fps) + 1, `the shoot holds ${seen.size} poses, not a continuum`);
  assert.ok(seen.size >= 8, "and it is a shoot, not a cut");
});

test("the glow lands on the LANDING step and on no other", () => {
  const fps = 24, landed = [];
  // HF-1: frame f is round(t * fps) === f, so the middle of frame f is f / fps
  for (let f = 0; f <= 40; f++) if (stop(f / fps).landed) landed.push(f);
  assert.equal(landed.length, 1, `exactly one landing frame, got ${landed}`);
  assert.equal(landed[0], Math.ceil(TOKYO.run_s * fps - 1e-9), "the first frame at or past the end of the shoot");
  assert.ok(stop(landed[0] / fps).u1 >= 1, "and the bar is at its number on it");
  assert.equal(stop((landed[0] - 1) / fps).landed, false);
  assert.equal(stop((landed[0] + 1) / fps).landed, false, "one frame only: the glow is a hit, not a state");
});

test("the stepped burst RESTS on the continuous one's frame: identical at and after the settle", () => {
  const end = TOKYO.run_s + TOKYO.settle_s;
  assert.equal(stop(end).u1, 1);
  assert.equal(stop(end).u2, 1, "the stepped run is clamped to its own end: it rests, it does not hang 2e-16 short");
  for (const run of [end + 1e-6, end + 0.04, end + 0.5, end + 3]) {
    const a = stop(run), b = cont(run);
    assert.equal(a.u1, b.u1, `u1 at run ${run}`);
    assert.equal(a.u2, b.u2, `u2 at run ${run}`);
    assert.equal(a.u2, 1);
  }
  // at EXACTLY the settle the continuous clock is (R + S - R) / S, which is 1 - 2e-16 in floating point.
  // The difference is 1e-14 of a pixel - the same frame to every decimal the page writes - and it is the
  // continuous burst's own arithmetic, left untouched on purpose.
  assert.ok(Math.abs(cont(end).u2 - 1) < 1e-12);
  assert.ok(stop(end - 1 / 24).u2 < 1, "and it is still settling one frame before");
});

test("the stepped clock never runs past the settle, so no step overshoots the resting frame", () => {
  const end = TOKYO.run_s + TOKYO.settle_s;
  for (let run = 0; run <= 3; run += 1 / 96) assert.ok(stop(run).t <= end + 1e-12, `t ran past the settle at ${run}`);
});

test("a hold-2 cadence steps the same way, half as often", () => {
  const cad = { hold: 2, fps: 12 };
  const seen = new Set();
  for (let run = 0; run < TOKYO.run_s; run += 1 / 480) seen.add(stop(run, cad).u1.toFixed(9));
  assert.ok(seen.size <= Math.ceil(TOKYO.run_s * 12) + 1, "on 2s holds half the poses");
  const end = TOKYO.run_s + TOKYO.settle_s;
  assert.equal(stop(end + 0.2, cad).u1, 1);
  assert.equal(stop(end + 0.2, cad).u2, 1);
});
