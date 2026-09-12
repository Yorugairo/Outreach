// P52 T9 - the melt exit (R26-15): the world sags into drips under the gooey threshold, balls up on 2s, and is
// thrown off the stage or splashed. Every assertion below is on the PURE math: the phases' shares, the sag's
// monotonicity, the ball's radius at the end of its phase, the splash's droplets, the throw's exit - and the one
// that the rest rests on, that meltState is a function of t and of nothing else.
import { test } from "node:test";
import assert from "node:assert/strict";
import { MELT, meltOpts, meltShares, meltPhase, meltBlur, meltDrips, meltDepth, meltTop, meltOutline, ballCircle, ballAt,
         ballFlat, splashDrops, splashFade, meltThrowAt, meltState, meltFilterMarkup, meltMaskMarkup } from "../../scripts/species/melt.mjs";
import { stepped } from "../../scripts/kinetics/stopaction.mjs";

// the engine's own seeded hash, bound the way the scene loop binds it: rnd(k) in [0, 1), never Math.random
const hash = (seed, i, salt) => {
  let h = (seed ^ Math.imul(i + 1, 0x9E3779B1) ^ Math.imul(salt + 1, 0x85EBCA77)) >>> 0;
  h = Math.imul(h ^ (h >>> 15), 0x2C1B3C6D); h = Math.imul(h ^ (h >>> 12), 0x297A2D39);
  return ((h ^ (h >>> 15)) >>> 0) / 4294967296;
};
const rnd = (k) => hash(0x3E17, k, 5);
const RECT = { x: 87, y: 49, w: 1745, h: 981 };          // a 1920x1080 stage's page box in the world's own px
const SB = { x: 87, y: 49, w: 1745, h: 981 };
const OPTS = (extra = {}) => Object.assign({ rect: RECT, stagebox: SB, secs: MELT.S }, extra);

// ---- the authored form -------------------------------------------------------------------------------------------
test("the exit's suffix is read as seconds, as splash, or as an x,y point - never guessed", () => {
  assert.equal(meltOpts("melt").secs, MELT.S, "a bare melt takes the default length");
  assert.equal(meltOpts("melt").splash, false, "and is a THROW: the splash is asked for by name");
  assert.deepEqual(meltOpts("melt").to, [MELT.TO[0], MELT.TO[1]]);
  assert.equal(meltOpts("melt:1.2").secs, 1.2);
  assert.equal(meltOpts("melt:splash").splash, true);
  assert.equal(meltOpts("melt:splash").secs, MELT.S, "splash says nothing about the length");
  assert.deepEqual(meltOpts("melt:0.92,1.18").to, [0.92, 1.18]);
  assert.equal(meltOpts("melt:0.92,1.18").secs, MELT.S, "an x,y is a POINT: the engine's exitSecs would have read 0.92 s");
  const both = meltOpts("melt:1.2:splash");
  assert.equal(both.secs, 1.2); assert.equal(both.splash, true);
  assert.throws(() => meltOpts("melt:sideways"), /neither a length/);
  assert.throws(() => meltOpts("melt:1,2,3"), /not an x,y point/);
  assert.throws(() => meltOpts("melt:-2"), /neither a length/);
});

// ---- the phases --------------------------------------------------------------------------------------------------
test("the four phases: three shares that sum to 1, and the fourth is the end", () => {
  const sh = meltShares();
  assert.equal(sh.length, 3);
  assert.ok(Math.abs(sh.reduce((a, b) => a + b, 0) - 1) < 1e-12, `the shares sum to ${sh.reduce((a, b) => a + b, 0)}`);
  assert.ok(sh.every((s) => s > 0), "no phase is empty");
  assert.equal(meltPhase(0).name, "melt");
  assert.equal(meltPhase(0.29).name, "melt");
  assert.equal(meltPhase(MELT.MELT_END).name, "ball");
  assert.equal(meltPhase(0.54).name, "ball");
  assert.equal(meltPhase(MELT.BALL_END).name, "fly");
  assert.equal(meltPhase(0.99).name, "fly");
  assert.equal(meltPhase(1).name, "gone");
  assert.equal(meltPhase(4).name, "gone");
  for (const u of [0, 0.15, 0.3, 0.45, 0.55, 0.8, 0.999]) {   // each phase's own clock runs 0 -> 1 inside it
    const ph = meltPhase(u);
    assert.ok(ph.k >= 0 && ph.k <= 1, `${u}: k out of range`);
    assert.ok(Math.abs((ph.from + ph.k * ph.span) - u) < 1e-12, `${u}: the phase's clock does not place it`);
  }
  assert.equal(meltPhase(0).k, 0);
  assert.ok(Math.abs(meltPhase(MELT.MELT_END - 1e-9).k - 1) < 1e-6, "the melt phase ends at 1");
});

test("the gooey blur rises over the melt and is exactly 0 once the ball has formed", () => {
  assert.equal(meltBlur(0), 0);
  assert.ok(meltBlur(0.15) > 0 && meltBlur(0.15) < MELT.BLUR);
  assert.ok(Math.abs(meltBlur(MELT.MELT_END - 1e-9) - MELT.BLUR) < 1e-3, "the peak is at the phase boundary");
  assert.ok(meltBlur(0.45) < MELT.BLUR && meltBlur(0.45) > 0, "it falls back through the ball phase");
  assert.ok(Math.abs(meltBlur(MELT.BALL_END - 1e-9)) < 1e-6, "a ball is solid, not a cloud");
  assert.equal(meltBlur(0.75), 0);
  assert.equal(meltBlur(1), 0);
});

// ---- the sag -----------------------------------------------------------------------------------------------------
test("the melting outline is a closed ring whose sag grows monotonically with u", () => {
  const foot = RECT.y + RECT.h;
  let last = -1, lastTop = -1;
  for (const k of [0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.75, 0.9, 1]) {
    const ring = meltOutline(RECT, k, rnd);
    assert.ok(ring.length >= 3, "a ring");
    assert.notDeepEqual(ring[0], ring[ring.length - 1], "closed IMPLICITLY - a ring never repeats its first vertex");
    assert.equal(ring[0][0], RECT.x, "the ring starts at the left edge");
    assert.equal(ring[MELT.TOP_N - 1][0], RECT.x + RECT.w, "and walks the top edge to the right one");
    if (k === 0) assert.deepEqual(ring[0], [RECT.x, RECT.y], "at u = 0 the ring IS the rect");
    assert.ok(ring[0][1] >= RECT.y - 1e-9, "the top edge only ever SINKS: a melting body loses height");
    const gaps = ring.map((p, i) => Math.hypot(p[0] - ring[(i + 1) % ring.length][0], p[1] - ring[(i + 1) % ring.length][1]));
    assert.ok(Math.max(...gaps) < RECT.w / 4, `a ${Math.max(...gaps).toFixed(0)} px gap between knots: the closed Catmull-Rom bulges across it`);
    for (const p of ring) {
      assert.ok(p[0] >= RECT.x - 1e-9 && p[0] <= RECT.x + RECT.w + 1e-9, "no vertex leaves the box sideways");
      assert.ok(p[1] >= RECT.y - 1e-9, "and none rises above the rect's own top edge");
    }
    const sunk = Math.min(...ring.map((p) => p[1])) - RECT.y;   /* how far the highest point of the body has sunk */
    assert.ok(sunk >= lastTop - 1e-9, `the top edge rose again at k=${k}`);
    assert.ok(sunk <= RECT.h * MELT.TOP_SAG + 1e-6, "and never past its dial");
    lastTop = sunk;
    const deepest = Math.max(...ring.map((p) => p[1])) - foot;
    assert.ok(deepest >= last - 1e-9, `the sag went back up at k=${k}: ${deepest} < ${last}`);
    if (k > 0.5) assert.ok(deepest > last + 1e-9, `the sag stalled at k=${k}`);
    last = deepest;
  }
  assert.ok(last <= RECT.h * (MELT.SAG + MELT.BASE_SAG) + 1e-6, "and it never hangs past its two dials");
  assert.ok(last > RECT.h * MELT.SAG * 0.5, "the deepest drip is a real drip");
});

test("every drip has its own place, size and start - all seeded, none random", () => {
  const d1 = meltDrips(RECT, rnd), d2 = meltDrips(RECT, rnd);
  assert.equal(d1.length, MELT.DRIPS);
  assert.deepEqual(d1, d2, "the same seed is the same drips");
  assert.ok(new Set(d1.map((d) => d.c)).size === MELT.DRIPS, "no two drips share a centre");
  assert.ok(d1.every((d) => d.c > RECT.x && d.c < RECT.x + RECT.w), "and all of them are on the edge");
  assert.ok(d1.some((d) => d.delay > 0.05), "the drips do not all open at once");
  assert.ok(Math.max(...d1.map((d) => d.delay)) <= MELT.DRIP_DELAY + 1e-9, "the last one still has most of the phase to run");
  const at = (x, k) => meltDepth(x, k, RECT, d1);
  assert.equal(at(RECT.x, 0), 0, "nothing hangs at u = 0");
  assert.ok(at(d1[0].c, 1) > at(d1[0].c + d1[0].w * 1.2, 1), "a drip is deepest at its own centre");
  assert.equal(meltTop(RECT.x, 0, RECT, d1), RECT.y, "and the top has not sunk at u = 0");
  const xs = []; for (let i = 0; i <= 40; i++) xs.push(RECT.x + RECT.w * (i / 40));
  const tops = xs.map((x) => meltTop(x, 1, RECT, d1));
  assert.ok(Math.max(...tops) - Math.min(...tops) > RECT.h * 0.03, "the sunk top is a WAVE, not a straight edge - it sinks furthest where the mass went");
  assert.ok(meltTop(RECT.x, 1, RECT, d1) > meltTop(RECT.x, 0.5, RECT, d1), "and it keeps sinking");
});

// ---- the ball ----------------------------------------------------------------------------------------------------
test("the outline balls up: at the end of the phase every vertex is BALL_R from the centroid", () => {
  const b0 = ballAt(RECT, 0, rnd), b1 = ballAt(RECT, 1, rnd);
  assert.ok(Math.abs(b1.r - MELT.BALL_R * RECT.h) < 1e-9, "the radius IS the dial");
  const rr = b1.outline.map((p) => Math.hypot(p[0] - b1.centre[0], p[1] - b1.centre[1]));
  assert.ok(Math.max(...rr) - Math.min(...rr) < 1e-6, "a circle, not a blob, at k = 1");
  assert.ok(Math.abs(Math.max(...rr) - b1.r) < 1e-6, `the ball's radius reaches BALL_R: ${Math.max(...rr)} vs ${b1.r}`);
  const spread0 = Math.max(...b0.outline.map((p) => Math.hypot(p[0] - b0.centre[0], p[1] - b0.centre[1])));
  assert.ok(spread0 > b1.r * 3, "at k = 0 it is still the page, not the ball");
  let last = Infinity;   // it contracts, never expands
  for (const k of [0, 0.25, 0.5, 0.75, 1]) {
    const b = ballAt(RECT, k, rnd);
    const far = Math.max(...b.outline.map((p) => Math.hypot(p[0] - b.centre[0], p[1] - b.centre[1])));
    assert.ok(far <= last + 1e-9, `the ball grew again at k=${k}`);
    last = far;
  }
  assert.deepEqual(ballAt(RECT, 0.4, rnd).outline, ballAt(RECT, 0.4, rnd).outline, "pure in k");
});

test("ballCircle is a circle and ballFlat squashes it about its own centre", () => {
  const c = [100, 200], ring = ballCircle(c, 30, 16);
  assert.equal(ring.length, 16);
  for (const p of ring) assert.ok(Math.abs(Math.hypot(p[0] - c[0], p[1] - c[1]) - 30) < 1e-9);
  const flat = ballFlat(ring, c, 1);
  const hy = Math.max(...flat.map((p) => Math.abs(p[1] - c[1]))), wx = Math.max(...flat.map((p) => Math.abs(p[0] - c[0])));
  assert.ok(Math.abs(hy - 30 * (1 - MELT.FLAT)) < 1e-9, "it loses exactly FLAT of its height");
  assert.ok(wx > 30, "and gains across");
  assert.deepEqual(ballFlat(ring, c, 0), ring, "and does nothing at k = 0");
});

// ---- the splash --------------------------------------------------------------------------------------------------
test("the splash throws DROPS droplets outward, each monotone along its own ray, all gone at k = 1", () => {
  const c = [900, 500], ks = [0, 0.2, 0.4, 0.6, 0.8, 1];
  const runs = ks.map((k) => splashDrops(c, RECT.h, k, rnd));
  for (const drops of runs) assert.equal(drops.length, MELT.DROPS, "the ring's count is the dial");
  for (let i = 0; i < MELT.DROPS; i++) {
    let last = -1;
    for (let j = 0; j < ks.length; j++) {
      const d = runs[j][i];
      assert.ok(d.d >= last - 1e-9, `droplet ${i} came back at k=${ks[j]}`);
      last = d.d;
    }
    assert.ok(last > 0, `droplet ${i} never left`);
    assert.ok(runs[0][i].d === 0, "and none of them is out before the burst");
  }
  assert.ok(runs[ks.length - 1].every((d) => d.alpha === 0), "every droplet has faded to nothing at k = 1");
  assert.ok(runs[1].every((d) => d.alpha === 1), "ink does not thin as it flies: it is at full strength on the way out");
  assert.ok(runs[4].every((d) => d.alpha > 0 && d.alpha < 1), "and is going by the end");
  for (let i = 0; i < MELT.DROPS; i++) {
    let a = 2;
    for (const drops of runs) { assert.ok(drops[i].alpha <= a + 1e-9, `droplet ${i} got darker again`); a = drops[i].alpha; }
  }
  const angles = runs[3].map((d) => d.a);
  assert.equal(new Set(angles).size, MELT.DROPS, "a RING: no two droplets on one ray");
  assert.ok(runs[4].every((d) => d.y > c[1] - RECT.h), "gravity pulls them down, never up out of the frame");
  assert.deepEqual(splashDrops(c, RECT.h, 0.5, rnd), splashDrops(c, RECT.h, 0.5, rnd), "seeded, not random");
});

// ---- the throw ---------------------------------------------------------------------------------------------------
test("the throw starts at rest and leaves the stage", () => {
  const to = { x: 1500, y: 900 }, F = 0.72;
  const a = meltThrowAt(0, to, F);
  assert.ok(Math.hypot(a.x, a.y) < 1e-9, "at k = 0 the ball is where the page was");
  const z = meltThrowAt(1, to, F);
  assert.ok(Math.abs(z.x - to.x) < 1e-6 && Math.abs(z.y - to.y) < 1e-6, "at k = 1 it is at the declared point");
  let last = -1;
  for (const k of [0, 0.2, 0.4, 0.6, 0.8, 1]) {
    const s = meltThrowAt(k, to, F);
    assert.ok(Math.hypot(s.x, s.y) >= last - 1e-9, `the flight doubled back at ${k}`);
    last = Math.hypot(s.x, s.y);
    if (k > 0) assert.equal(s.phase, "flight", "it never lands: a thrown page has no landing on this stage");
  }
  assert.ok(Math.abs(meltThrowAt(0.5, to, F).rot) > 0, "and it tumbles on the way out");
});

test("the whole ball leaves the stage by the end of a default melt", () => {
  const st = meltState(4.0, 4.0 + MELT.S * 0.999, OPTS(), rnd);
  assert.equal(st.phase, "fly");
  const cx = st.centre[0] + st.xf.x, cy = st.centre[1] + st.xf.y;
  const out = cx - st.r > SB.x + SB.w || cy - st.r > SB.y + SB.h || cx + st.r < SB.x || cy + st.r < SB.y;
  assert.ok(out, `the ball is still on the stage at (${cx.toFixed(0)}, ${cy.toFixed(0)}) r=${st.r.toFixed(0)}`);
});

// ---- the state ---------------------------------------------------------------------------------------------------
test("meltState is a pure function of t: the same instant twice is the same object", () => {
  for (const u of [0, 0.1, 0.3, 0.45, 0.55, 0.7, 0.95, 1.2]) {
    const t = 4.0 + u * MELT.S;
    const a = meltState(4.0, t, OPTS(), rnd), b = meltState(4.0, t, OPTS(), rnd);
    assert.deepEqual(a, b, `u=${u} is not a pure function of t`);
    const c = meltState(4.0, t, OPTS({ splash: true }), rnd), d = meltState(4.0, t, OPTS({ splash: true }), rnd);
    assert.deepEqual(c, d, `u=${u} (splash) is not a pure function of t`);
  }
});

test("meltState walks the four phases and hands the painter what each one needs", () => {
  const t0 = 4.0, at = (u, extra) => meltState(t0, t0 + u * MELT.S, OPTS(extra), rnd);
  const m = at(0.15);
  assert.equal(m.phase, "melt");
  assert.ok(m.blur > 0 && m.path.startsWith("M") && m.path.endsWith("Z"), "a closed path and a blur");
  assert.equal(m.xf, null); assert.equal(m.drops.length, 0); assert.equal(m.opacity, 1);
  const b = at(0.45);
  assert.equal(b.phase, "ball");
  assert.ok(b.r > 0 && b.centre.length === 2 && b.path.length > 0);
  assert.equal(b.xf, null);
  const f = at(0.75);
  assert.equal(f.phase, "fly");
  assert.ok(f.xf && Math.hypot(f.xf.x, f.xf.y) > 0, "the throw is under way");
  assert.equal(f.drops.length, 0, "a throw has no droplets");
  const s = at(0.75, { splash: true });
  assert.equal(s.xf, null, "a splash does not travel");
  assert.equal(s.drops.length, MELT.DROPS);
  assert.ok(s.flat < 1, "the ball flattens as it bursts");
  assert.ok(at(0.999, { splash: true }).opacity < 0.35, "and is all but gone by the end of its own clock");
  assert.equal(splashFade(1), 0, "which is exactly nothing when that clock reaches 1");
  assert.equal(splashFade(0), 1);
  assert.equal(splashFade(MELT.FADE_FROM), 1, "the ink holds until FADE_FROM, then goes");
  const g = at(1.0);
  assert.equal(g.phase, "gone");
  assert.equal(g.gone, true); assert.equal(g.opacity, 0);
  assert.equal(at(2.0).phase, "gone", "and it stays gone");
});

test("the ball and the flight ride the STEPPED clock - on 2s, the integer frame index", () => {
  const t0 = 4.0, seen = new Set();
  const fps = MELT.FPS, ballFrom = t0 + MELT.MELT_END * MELT.S;
  for (let f = 0; f < Math.round((MELT.BALL_END - MELT.MELT_END) * MELT.S * fps); f++) {
    seen.add(meltState(t0, ballFrom + f / fps, OPTS(), rnd).k.toFixed(9));
  }
  const frames = Math.round((MELT.BALL_END - MELT.MELT_END) * MELT.S * fps);
  assert.ok(seen.size <= Math.ceil(frames / MELT.HOLD) + 1, `${seen.size} distinct poses over ${frames} frames: not on 2s`);
  assert.ok(seen.size > 1, "and it does move");
  // the quantisation IS stopaction's, not a second implementation
  const span = (MELT.BALL_END - MELT.MELT_END) * MELT.S, tl = 0.1875;
  assert.ok(Math.abs(meltState(t0, ballFrom + tl, OPTS(), rnd).k - stepped(tl, MELT.HOLD, fps) / span) < 1e-12);
});

test("the melt phase is NOT stepped: a sag is a liquid, and liquid does not step", () => {
  const t0 = 4.0, ks = [];
  for (let f = 0; f < 6; f++) ks.push(meltState(t0, t0 + f / MELT.FPS, OPTS(), rnd).k);
  assert.equal(new Set(ks).size, 6, "every frame of the sag is its own");
});

// ---- the markup --------------------------------------------------------------------------------------------------
test("the filter is a blur under an alpha ramp, and the mask is one filtered path", () => {
  const f = meltFilterMarkup("meltf", 0.15);
  assert.ok(f.includes('id="meltf"'));
  assert.ok(/<feGaussianBlur stdDeviation="\d+\.\d\d"\/>/.test(f), f);
  assert.ok(f.includes('slope="' + MELT.EDGE_SLOPE + '"'), "the gooey threshold");
  assert.ok(f.indexOf("feGaussianBlur") < f.indexOf("feFuncA"), "blur FIRST, then the ramp - the other way round is a fade");
  assert.ok(!f.includes("feColorMatrix"), "the K-M colour stages would flatten the world to a silhouette");
  const m = meltMaskMarkup("meltm", "meltf");
  assert.ok(m.includes('<mask id="meltm"') && m.includes('filter="url(#meltf)"') && m.includes('fill="#fff"'));
  assert.ok(m.includes('maskUnits="objectBoundingBox"'));
});
