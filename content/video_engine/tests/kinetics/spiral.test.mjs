// P57 T22 / R26-101 - THE PAGE VORTEX PROMOTED (the P55 T7 recipe). The promotion's proof is that every golden
// is byte-identical, so what this file pins is that the module still carries the INLINE ENGINE's numbers and
// arithmetic - and above all THE GROUPING DECISION: one geometry, two clocks. The retract and the return are
// asserted to be the SAME map at the same u, because that is the reason this module holds both directions and
// both cards (`page_enter:spiral`, `page_exit:retract`) point at it. The instants are the `spiral-return`
// golden's own (FRAME_T 16.12, @proof-retract 13.5, @proof-fade 14.5), so the three frames the parent read are
// pinned here as numbers as well as pixels.
import { test } from "node:test";
import assert from "node:assert/strict";
import { LP_RETRACT, spiralClocks, lpVortex, lpVortexCss, lpVortexSvg, spiralLineWidth,
         lpSpiral, lpParticles } from "../../scripts/species/spiral.mjs";

const near = (a, b, eps = 1e-12) => Math.abs(a - b) <= eps;
const C = { x: 960, y: 540 };                 // a drain at the stage's centre
const RMAX = Math.hypot(1920, 1080) / 2;      // the page's own Rmax, as lpParticles computes it
// the `spiral-return` golden's clock (tests/golden/build_golden_sources.py SPIRAL_CUT / render_baseline PROOF_FRAMES)
const A = 15.0, Z = 15.0, RUN = 30.0, FRAME_T = 15.0 + 0.70 * 1.6, RETRACT_T = 13.5, FADE_T = 14.5;

// ---------------------------------------------------------------- the dials, as the inline code carried them
test("every dial is the inline engine's literal, to the digit, and frozen", () => {
  assert.ok(Object.isFrozen(LP_RETRACT));
  assert.equal(LP_RETRACT.COLOURS, 1.0, "const LP_RETRACT = { COLOURS: 1.0, ...");
  assert.equal(LP_RETRACT.CHARCOAL, 1.0, "... CHARCOAL: 1.0 ...");
  assert.equal(LP_RETRACT.IN, 1.6, "... IN: 1.6 ...");
  assert.equal(LP_RETRACT.TURNS, 3.0, '... TURNS: 3.0 ("a way tighter vortex, almost celestial" - three turns)');
  assert.equal(LP_RETRACT.LAG, 0.25, "... LAG: 0.25 ...");
  assert.equal(LP_RETRACT.ALPHA, 0.85, "... ALPHA: 0.85 ...");
  assert.equal(LP_RETRACT.RECT_FADE, 0.3, "... RECT_FADE: 0.3 }");
  assert.equal(LP_RETRACT.R_FALL, 1.7, "rr = r * (1 - Math.pow(ui, 1.7))");
  assert.equal(LP_RETRACT.CORE_BASE, 0.4, "th = TURNS * 2pi * ui * (0.4 + 1.6 * Math.pow(1 - rn, 1.5))");
  assert.equal(LP_RETRACT.CORE_GAIN, 1.6, "... the core's own 1.6 ...");
  assert.equal(LP_RETRACT.CORE_FALL, 1.5, "... on (1 - rn) ** 1.5");
  assert.equal(LP_RETRACT.SHRINK, 0.7, "s = Math.pow(1 - ui, 0.7)");
  assert.equal(LP_RETRACT.IN_FIELD, 0.55, "uf = Math.max(uf, 1 - clamp01(ui / 0.55))");
  assert.equal(LP_RETRACT.IN_COLOUR_AT, 0.4, "uc = Math.max(uc, 1 - clamp01((ui - 0.4) / 0.6))");
  assert.equal(LP_RETRACT.IN_COLOUR_S, 0.6, "... the same expression's 0.6");
  assert.equal(LP_RETRACT.LINE_W, 8, "strokeWidth = (8 * Math.pow(1 - Math.min(1, uc * 1.15), 0.7) + 0.5)");
  assert.equal(LP_RETRACT.LINE_RATE, 1.15, "... the same expression's 1.15 ...");
  assert.equal(LP_RETRACT.LINE_FALL, 0.7, "... its 0.7 ...");
  assert.equal(LP_RETRACT.LINE_MIN, 0.5, "... and its floor of 0.5");
});

// ---------------------------------------------------------------- THE TWO CLOCKS (the grouping decision)
test("the RETRACT runs off the scene's END: nothing until z - COLOURS - CHARCOAL, then both phases in turn", () => {
  assert.deepEqual(spiralClocks(12.99, 0, Z, undefined, undefined), { uc: 0, uf: 0 }, "before 13.0 the page is untouched");
  assert.deepEqual(spiralClocks(RETRACT_T, 0, Z, undefined, undefined), { uc: 0.5, uf: 0 },
                   "@proof-retract: phase one half done, the field still home");
  assert.deepEqual(spiralClocks(14.0, 0, Z, undefined, undefined), { uc: 1, uf: 0 }, "the colours are gone as phase two opens");
  assert.deepEqual(spiralClocks(FADE_T, 0, Z, undefined, undefined), { uc: 1, uf: 0.5 }, "@proof-fade: phase two half done");
  assert.deepEqual(spiralClocks(Z, 0, Z, undefined, undefined), { uc: 1, uf: 1 }, "bare cream at the cut");
});

test('exit "cut" skips the retract entirely (E40 #5: the punch lands on the last line)', () => {
  for (const t of [13.0, RETRACT_T, 14.0, FADE_T, Z]) {
    assert.deepEqual(spiralClocks(t, 0, Z, "cut", undefined), { uc: 0, uf: 0 }, `t=${t} is untouched`);
  }
});

test('enter "spiral" runs the SAME clocks backwards off the scene\'s START - the field surfaces first', () => {
  assert.deepEqual(spiralClocks(A, A, RUN, "cut", "spiral"), { uc: 1, uf: 1 }, "the page arrives fully down the drain");
  const mid = spiralClocks(FRAME_T, A, RUN, "cut", "spiral");
  assert.ok(near(mid.uc, 0.5), `the golden's instant is the colours half unwound (uc ${mid.uc})`);
  assert.equal(mid.uf, 0, "and the field already surfaced - IN_FIELD 0.55 of 1.6 s is 0.88 s, long past");
  assert.equal(spiralClocks(A + 0.88, A, RUN, "cut", "spiral").uf, 0, "the stains are home at ui = IN_FIELD");
  assert.deepEqual(spiralClocks(A + LP_RETRACT.IN, A, RUN, "cut", "spiral"), { uc: 0, uf: 0 }, "the page stands at IN");
  assert.ok(spiralClocks(A + 0.2, A, RUN, "cut", "spiral").uc > spiralClocks(A + 1.2, A, RUN, "cut", "spiral").uc,
            "the return only ever unwinds");
});

test("ONE geometry, two directions: the retract at u and the return at the same u are the same map", () => {
  const out = spiralClocks(RETRACT_T, 0, Z, undefined, undefined);        // leaving, uc 0.5
  const back = spiralClocks(FRAME_T, A, RUN, "cut", "spiral");            // coming back, uc 0.5
  assert.ok(near(out.uc, back.uc, 1e-9), "the two goldens are read at the same point of one map");
  const a = lpVortex(300, 200, C, RMAX, out.uc), b = lpVortex(300, 200, C, RMAX, back.uc);
  for (const k of Object.keys(a)) {
    assert.ok(near(a[k], b[k], 1e-9), `the same particle stands in the same ${k} both ways - which is why one module holds both`);
  }
});

// ---------------------------------------------------------------- THE MAP: the parametric path over u
test("u = 0 is the identity: every particle at home, unturned, unstretched", () => {
  for (const [x, y] of [[300, 200], [1700, 900]]) {
    const v = lpVortex(x, y, C, RMAX, 0);
    assert.ok(near(v.x, x, 1e-9) && near(v.y, y, 1e-9), `${x},${y} is home`);
    assert.equal(v.th, 0);
    assert.equal(v.sx, 1);
    assert.equal(v.sy, 1);
  }
  const drain = lpVortex(C.x, C.y, C, RMAX, 0);   // r = 0 is the one guarded case: `Math.hypot(dx, dy) || 1e-6`
  assert.ok(near(drain.x, C.x, 1e-6) && near(drain.y, C.y, 1e-6), "a particle ON the drain moves by the guard, not by the map");
});

test("u = 1 takes every particle to the drain and shrinks it to nothing", () => {
  const v = lpVortex(300, 200, C, RMAX, 1);
  assert.ok(near(v.x, C.x, 1e-9) && near(v.y, C.y, 1e-9), "at the board centre");
  assert.equal(v.sx, 0);
  assert.equal(v.sy, 0);
});

test("the drain takes the CENTRE first: LAG delays a particle by its normalised radius", () => {
  const rim = lpVortex(1920, 1080, C, RMAX, 0.2), core = lpVortex(1000, 560, C, RMAX, 0.2);
  assert.equal(rim.ui, 0, "a particle at Rmax has not started at u = LAG * 1");
  assert.ok(core.ui > rim.ui, "one beside the drain is already on its way");
  assert.equal(lpVortex(1920, 1080, C, RMAX, LP_RETRACT.LAG).ui, 0, "the rim starts exactly at u = LAG ...");
  assert.ok(lpVortex(1920, 1080, C, RMAX, LP_RETRACT.LAG + 1e-6).ui > 0, "... and not before");
  const rn = Math.hypot(40, 20) / RMAX;   // (1000, 560) is 40, 20 off the drain
  assert.ok(near(lpVortex(1000, 560, C, RMAX, 0.25).ui, (0.25 - LP_RETRACT.LAG * rn) / (1 - LP_RETRACT.LAG), 1e-12),
            "while a particle near the drain is already a third of the way in at u = LAG: (u - LAG*rn) / (1 - LAG)");
});

test("the radius falls slowly, then fast (R_FALL 1.7), and never overshoots the drain", () => {
  const r0 = Math.hypot(300 - C.x, 200 - C.y);
  let prev = r0;
  for (let u = 0; u <= 1.0001; u += 0.05) {
    const v = lpVortex(300, 200, C, RMAX, u), r = Math.hypot(v.x - C.x, v.y - C.y);
    assert.ok(r <= prev + 1e-9, `r falls monotonically at u=${u.toFixed(2)}`);
    assert.ok(r >= -1e-9, "and never past the drain");
    prev = r;
  }
  const ui = 0.5, expected = r0 * (1 - Math.pow(ui, LP_RETRACT.R_FALL));
  const at = lpVortex(300, 200, C, RMAX, LP_RETRACT.LAG * Math.min(1, r0 / RMAX) + ui * (1 - LP_RETRACT.LAG));
  assert.ok(near(Math.hypot(at.x - C.x, at.y - C.y), expected, 1e-9), "r' = r * (1 - ui^1.7), exactly");
});

test("the whirl is DIFFERENTIAL: the core turns far more than the rim, and every radius between", () => {
  const rim = lpVortex(C.x + RMAX, C.y, C, RMAX, 1), core = lpVortex(C.x + 1, C.y, C, RMAX, 1);
  assert.ok(near(rim.th, LP_RETRACT.TURNS * 360 * LP_RETRACT.CORE_BASE), "the rim: TURNS * CORE_BASE turns");
  assert.ok(near(core.th, LP_RETRACT.TURNS * 360 * (LP_RETRACT.CORE_BASE + LP_RETRACT.CORE_GAIN), 3),
            "the core: within 3 deg of TURNS * (CORE_BASE + CORE_GAIN) turns - a particle 1 px out is not quite the centre");
  assert.ok(near(core.th / rim.th, (LP_RETRACT.CORE_BASE + LP_RETRACT.CORE_GAIN) / LP_RETRACT.CORE_BASE, 0.01),
            "the ratio the dials carry, the engine's own '~4x the rim'");
  let prev = Infinity;
  for (let f = 0.02; f <= 1.0001; f += 0.02) {   // the turn falls monotonically outward: arms, never a wheel
    const th = lpVortex(C.x + f * RMAX, C.y, C, RMAX, 1).th;
    assert.ok(th <= prev + 1e-9, `the turn falls with the radius at rn=${f.toFixed(2)}`);
    prev = th;
  }
});

test("the stretch along the flow is AREA-PRESERVING, and peaks at ui = 0.5", () => {
  for (let u = 0; u <= 1.0001; u += 0.05) {
    const v = lpVortex(300, 200, C, RMAX, u), s = Math.pow(1 - v.ui, LP_RETRACT.SHRINK);
    assert.ok(near(v.sx * v.sy, s * s, 1e-12), `sx * sy = s^2 at u=${u.toFixed(2)} (det of diag(1+a, 1/(1+a)) is 1)`);
  }
  const half = lpVortex(C.x + 400, C.y, C, RMAX, LP_RETRACT.LAG * (400 / RMAX) + 0.5 * (1 - LP_RETRACT.LAG));
  const s = Math.pow(0.5, LP_RETRACT.SHRINK), a = LP_RETRACT.ALPHA * 4 * 0.5 * 0.5;
  assert.ok(near(half.sx, s * (1 + a), 1e-12) && near(half.sy, s / (1 + a), 1e-12), "a = ALPHA * 4ui(1-ui) = ALPHA at ui 0.5");
});

test("the tangent is 90 degrees off the ray, so the stretch lies ALONG the flow", () => {
  const v = lpVortex(300, 200, C, RMAX, 0.4);
  assert.ok(near(v.tan - v.th, Math.atan2(200 - C.y, 300 - C.x) * 180 / Math.PI + 90, 1e-9));
});

// ---------------------------------------------------------------- the two transforms of one map
test("the CSS transform is the particle's own centre, the SVG one is in user units", () => {
  const v = lpVortex(300, 200, C, RMAX, 0.4);
  assert.equal(lpVortexCss(v, 300, 200),
    "translate(" + (v.x - 300).toFixed(2) + "px," + (v.y - 200).toFixed(2) + "px) rotate(" + v.tan.toFixed(2) +
    "deg) scale(" + v.sx.toFixed(4) + "," + v.sy.toFixed(4) + ") rotate(" + (v.th - v.tan).toFixed(2) + "deg)");
  assert.equal(lpVortexSvg(v, 300, 200),
    "translate(" + v.x.toFixed(2) + " " + v.y.toFixed(2) + ") rotate(" + v.tan.toFixed(2) + ") scale(" +
    v.sx.toFixed(4) + " " + v.sy.toFixed(4) + ") rotate(" + (v.th - v.tan).toFixed(2) + ") translate(-300.00 -200.00)");
  const home = lpVortex(C.x + 400, C.y, C, RMAX, 0);   // on the ray phi = 0, so the tangent is a plain 90 deg
  assert.equal(lpVortexCss(home, C.x + 400, C.y), "translate(0.00px,0.00px) rotate(90.00deg) scale(1.0000,1.0000) rotate(-90.00deg)",
               "at u = 0 the CSS transform is the identity, written out: no move, no net turn, no stretch");
});

// ---------------------------------------------------------------- the series line's own thinning
test("the noodle thins from LINE_W to LINE_MIN and reaches the floor at 1 / LINE_RATE", () => {
  assert.equal(spiralLineWidth(0), "8.50", "8 * 1 + 0.5 at rest");
  assert.equal(spiralLineWidth(1 / LP_RETRACT.LINE_RATE), "0.50", "the floor, before the drain is reached");
  assert.equal(spiralLineWidth(1), "0.50", "and it stays there");
  assert.equal(spiralLineWidth(0.5), (8 * Math.pow(1 - 0.575, 0.7) + 0.5).toFixed(2), "the inline expression, to the digit");
  let prev = 9;
  for (let u = 0; u <= 1.0001; u += 0.02) {
    const w = Number(spiralLineWidth(u));
    assert.ok(w <= prev + 1e-9 && w >= LP_RETRACT.LINE_MIN, `monotone and floored at u=${u.toFixed(2)}`);
    prev = w;
  }
});

// ---------------------------------------------------------------- the painter's one law that is not geometry
test("an IDLE frame touches no style and reads no layout (the sub-pixel re-snap E45 found)", () => {
  let touched = 0;
  const st = { get glyphs() { touched++; return []; }, get page() { touched++; return {}; },
               get rect() { touched++; return {}; }, get blobs() { touched++; return []; } };
  const scene = { span: [0, RUN] };
  lpSpiral(st, scene, 5.0, { exit: "cut" });     // no retract, no spiral entry: nothing to do
  assert.equal(touched, 0, "the early-out returns before it reads anything off the page");
  assert.equal(st.parts, undefined, "and measures no particles");
});

test("lpParticles is the module's, not the engine's - the painter measures through it", () => {
  assert.equal(typeof lpParticles, "function");
  assert.equal(typeof lpSpiral, "function");
});
