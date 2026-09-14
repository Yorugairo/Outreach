// P52 T9 - the melt exit (R26-15), reworked to E88 (R26-76): the CHART'S INK sags and runs under the gooey threshold,
// is squeezed into a dense heavy ball on 2s, and ends one of three authored ways - thrown (the next chart draws on the
// same board), splashed into the next chart, or splashed into a narrative plate. The board never melts. Every assertion
// below is on the PURE math, and the one the rest rests on: meltState is a function of t and of nothing else.
import { test } from "node:test";
import assert from "node:assert/strict";
import { MELT, MELT_ENDINGS, MELT_CSS, meltOpts, meltShares, meltPhase, meltBlur, meltRelease, meltDrawDelay, meltDrips,
         meltDepth, meltTop, meltOutline, meltRun, ballCircle, ballAt, meltSqueeze, meltBodyAlpha, ballFlat, meltSettle,
         meltMixInk, splashDrops, splashStains, meltThrowAt, meltState, meltFilterMarkup, meltMaskMarkup,
         meltInkFilterMarkup, meltRevealMarkup, meltBodyTransform, meltIsBoard, meltInkOf, meltTint, meltSplatPath, splashSats,
         meltSpring, meltBodyGrow, meltTextFilterMarkup, MELT_MATERIALS, meltWeightShare, meltWeightMass, meltWeightAt,
         meltRollDir, meltMarkAt, meltBallRing } from "../../scripts/species/melt.mjs";
import { stepped, MASS, STOP, rollXf } from "../../scripts/kinetics/stopaction.mjs";
import { DROP, dropArea } from "../../scripts/kinetics/drop.mjs";
import { hexToLin } from "../../scripts/kinetics/ink.mjs";

const hash = (seed, i, salt) => {
  let h = (seed ^ Math.imul(i + 1, 0x9E3779B1) ^ Math.imul(salt + 1, 0x85EBCA77)) >>> 0;
  h = Math.imul(h ^ (h >>> 15), 0x2C1B3C6D); h = Math.imul(h ^ (h >>> 12), 0x297A2D39);
  return ((h ^ (h >>> 15)) >>> 0) / 4294967296;
};
const rnd = (k) => hash(0x3E17, k, 5);
const RECT = { x: 190, y: 120, w: 1540, h: 830 };          // the INK box: the chart's marks on a 1920x1080 page's board
const SB = { x: 96, y: 54, w: 1920, h: 1080 };
const OPTS = (extra = {}) => Object.assign({ rect: RECT, stagebox: SB, secs: MELT.S, ending: "throw" }, extra);
const lum = (hex) => { const l = hexToLin(hex); return 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2]; };

// ---- the authored form -------------------------------------------------------------------------------------------
test("E88's grammar: throw is the default, a splash names its ending, and a bare splash is refused", () => {
  assert.deepEqual(MELT_ENDINGS, ["throw", "splash:chart", "splash:plate"]);
  assert.equal(meltOpts("melt").ending, "throw", "a bare melt is a THROW");
  assert.equal(meltOpts("melt").secs, MELT.S);
  assert.deepEqual(meltOpts("melt").to, [MELT.TO[0], MELT.TO[1]]);
  assert.equal(meltOpts("melt:throw").ending, "throw");
  assert.equal(meltOpts("melt:splash:chart").ending, "splash:chart");
  assert.equal(meltOpts("melt:splash:plate").ending, "splash:plate");
  assert.equal(meltOpts("melt:1.2:splash:plate").secs, 1.2);
  assert.equal(meltOpts("melt:splash:chart:1.2").ending, "splash:chart");
  assert.equal(meltOpts("melt:splash:chart:1.2").secs, 1.2);
  assert.deepEqual(meltOpts("melt:throw:0.92,1.18").to, [0.92, 1.18]);
  assert.equal(meltOpts("melt:0.92,1.18").secs, MELT.S, "an x,y is a POINT, never 0.92 s");
  assert.throws(() => meltOpts("melt:splash"), /splash names no ending since E88/);
  assert.throws(() => meltOpts("melt:splash:sideways"), /splash names no ending/);
  assert.throws(() => meltOpts("melt:chart"), /a splash's ending/);
  assert.throws(() => meltOpts("melt:throw:splash:chart"), /two endings/);
  assert.throws(() => meltOpts("melt:splash:plate:0.5,0.5"), /where a THROW goes/);
  assert.throws(() => meltOpts("melt:sideways"), /neither a length/);
  assert.throws(() => meltOpts("melt:1,2,3"), /not an x,y point/);
  assert.throws(() => meltOpts("melt:-2"), /neither a length/);
});

// ---- the board is not the ink --------------------------------------------------------------------------------------
test("the board and the ink are split by class: grain, roll edge, field and field plate are the board", () => {
  const node = (cls) => ({ classList: { contains: (c) => cls.split(" ").includes(c) } });
  for (const c of ["lp-grain", "lp-edge", "lp-field", "lp-fieldplate"]) assert.ok(meltIsBoard(node(c)), c);
  for (const c of ["lp-chart", "lp-ink lp-title", "lp-rail", "lp-chart lp-perform", "lp-ink lp-sub lp-note"]) assert.ok(!meltIsBoard(node(c)), c);
  assert.ok(MELT_CSS.includes(".meltink .lp-field") && MELT_CSS.includes(".meltink .lp-page{background:transparent"), "the ink clone hides the board and the cream");
  assert.ok(MELT_CSS.includes(".meltboard .lp-page>:not(.lp-grain):not(.lp-edge):not(.lp-field):not(.lp-fieldplate)"), "the board world hides everything else");
  assert.ok(MELT_CSS.includes(".meltink .lp-ink,.meltink .lp-rail,.meltink .lp-chart line,.meltink .lp-chart text{visibility:hidden"), "the marks clone never draws the words or the rules");
  assert.ok(MELT_CSS.includes(".melttext .lp-chart text *{visibility:visible"), "the text clone draws only the words");
  const tf = meltTextFilterMarkup("meltx");
  assert.ok(tf.includes('stdDeviation="0 0"') && !tf.includes("feFlood"), "a glyph runs down a VERTICAL-only blur, untinted - it never swells into its box");
  assert.equal((tf.match(/<feOffset /g) || []).length, 1, "ONE streak, never stacked copies of the word");
  assert.ok(tf.lastIndexOf('in="SourceGraphic"/>') > tf.indexOf("<feMerge>"), "the crisp glyph is drawn over its streak, legible at its top");
});

// ---- the phases --------------------------------------------------------------------------------------------------
test("the four phases: three shares that sum to 1, and the fourth is the end", () => {
  const sh = meltShares();   /* four now (R26-118): melt, ball, WEIGHT, the ending - and the weight's is exactly 0
                                unless the exit asked for it, which is why every melt that shipped is untouched */
  assert.ok(Math.abs(sh.reduce((a, b) => a + b, 0) - 1) < 1e-12);
  assert.equal(sh[2], 0, "no weight phase unless `melt:weight` says so");
  assert.ok([sh[0], sh[1], sh[3]].every((s) => s > 0));
  assert.equal(meltPhase(0.29).name, "melt");
  assert.equal(meltPhase(MELT.MELT_END).name, "ball");
  assert.equal(meltPhase(MELT.BALL_END).name, "fly");
  assert.equal(meltPhase(1).name, "gone");
  for (const u of [0, 0.15, 0.3, 0.45, 0.55, 0.8, 0.999]) {
    const ph = meltPhase(u);
    assert.ok(Math.abs((ph.from + ph.k * ph.span) - u) < 1e-12, `${u}`);
  }
  assert.equal(meltBlur(0), 0);
  assert.ok(Math.abs(meltBlur(MELT.MELT_END - 1e-9) - MELT.BLUR) < 1e-3);
  assert.ok(Math.abs(meltBlur(MELT.BALL_END - 1e-9)) < 1e-6, "a ball is solid, not a cloud");
});

// ---- the sag and the run -----------------------------------------------------------------------------------------
test("the ink box's outline sags monotonically and never leaves the box sideways", () => {
  const foot = RECT.y + RECT.h;
  let last = -1, lastTop = -1;
  for (const k of [0, 0.2, 0.45, 0.75, 1]) {
    const ring = meltOutline(RECT, k, rnd);
    if (k === 0) assert.deepEqual(ring[0], [RECT.x, RECT.y]);
    for (const p of ring) assert.ok(p[0] >= RECT.x - 1e-9 && p[0] <= RECT.x + RECT.w + 1e-9 && p[1] >= RECT.y - 1e-9);
    const sunk = Math.min(...ring.map((p) => p[1])) - RECT.y, deepest = Math.max(...ring.map((p) => p[1])) - foot;
    assert.ok(sunk >= lastTop - 1e-9 && deepest >= last - 1e-9, `k=${k}`);
    lastTop = sunk; last = deepest;
  }
  const d = meltDrips(RECT, rnd);
  assert.deepEqual(d, meltDrips(RECT, rnd), "seeded");
  assert.equal(meltDepth(RECT.x, 0, RECT, d), 0);
  assert.equal(meltTop(RECT.x, 0, RECT, d), RECT.y);
});

test("the marks RUN: the smear grows over the sag and drains back into the ball", () => {
  assert.equal(meltRun("melt", 0, RECT), 0);
  let last = -1;
  for (const k of [0, 0.25, 0.5, 0.75, 1]) { const r = meltRun("melt", k, RECT); assert.ok(r >= last); last = r; }
  assert.ok(Math.abs(last - MELT.RUN * RECT.h) < 1e-9, "the run reaches its dial at the sag's end");
  assert.ok(Math.abs(meltRun("ball", 0, RECT) - last) < 1e-9, "continuous into the ball");
  assert.equal(meltRun("ball", 1, RECT), 0, "and gone once the ball is formed");
  assert.equal(meltRun("fly", 0.5, RECT), 0);
});

// ---- the ball ----------------------------------------------------------------------------------------------------
test("the ball is dense: smaller than P52 T9's, a circle of BALL_R at the end of its phase", () => {
  assert.ok(MELT.BALL_R < 0.15, "smaller than the whole-page melt's ball");
  const b1 = ballAt(RECT, 1, rnd);
  const rr = b1.outline.map((p) => Math.hypot(p[0] - b1.centre[0], p[1] - b1.centre[1]));
  assert.ok(Math.max(...rr) - Math.min(...rr) < 1e-6 && Math.abs(Math.max(...rr) - MELT.BALL_R * RECT.h) < 1e-6);
  let last = Infinity;
  for (const k of [0, 0.25, 0.5, 0.75, 1]) {
    const b = ballAt(RECT, k, rnd), far = Math.max(...b.outline.map((p) => Math.hypot(p[0] - b.centre[0], p[1] - b.centre[1])));
    assert.ok(far <= last + 1e-9); last = far;
  }
});

test("the ink is SQUEEZED into the ball, not cropped by it, and the body comes up solid before it moves", () => {
  const r = MELT.BALL_R * RECT.h;
  assert.equal(meltSqueeze(RECT, r, 0), 1);
  const end = meltSqueeze(RECT, r, 1);
  assert.ok(Math.abs(end * Math.max(RECT.w, RECT.h) - MELT.SQUEEZE * 2 * r) < 1e-6, "the box's longer side ends at SQUEEZE diameters");
  let last = 2;
  for (const k of [0, 0.3, 0.6, 1]) { const s = meltSqueeze(RECT, r, k); assert.ok(s <= last + 1e-12); last = s; }
  assert.equal(meltBodyAlpha(0), 0);
  assert.equal(meltBodyGrow(0), MELT.BODY_SEED);
  assert.equal(meltBodyGrow(MELT.BODY_GROW), 1, "whole by BODY_GROW");
  const at45 = meltState(4.0, 4.0 + 0.45 * MELT.S, OPTS(), rnd);
  assert.ok(at45.bodyAlpha === 1 && at45.inkOpacity === 0, "by 045 the chart is a round, solid ball and nothing else");
  const nums45 = at45.body.match(/-?\d+(\.\d+)?/g).map(Number), rr45 = [];
  for (let i = 0; i + 1 < nums45.length; i += 2) rr45.push(Math.hypot(nums45[i] - at45.centre[0], nums45[i + 1] - at45.centre[1]));
  assert.ok(Math.abs(Math.max(...rr45) - at45.r) < at45.r * 0.05, "at its full radius");
  assert.ok(meltState(4.0, 4.0 + 0.15 * MELT.S, OPTS(), rnd).textOpacity > 0.3 && meltState(4.0, 4.0 + 0.45 * MELT.S, OPTS(), rnd).textOpacity === 0, "the words run and are gone by the ball");
  assert.equal(meltBodyAlpha(MELT.BODY_TO), 1, "solid from BODY_TO");
  assert.equal(meltBodyAlpha(1), 1);
  const t0 = 4.0, at = (u) => meltState(t0, t0 + u * MELT.S, OPTS(), rnd);
  const b = at(0.45);
  assert.equal(b.phase, "ball");
  assert.ok(b.scale < 1 && b.body.length > 0, "mid-ball: squeezed, with a body");
  const c = b.centre, bodyFar = Math.max(...b.bodyOutline.map((p) => Math.hypot(p[0] - c[0], p[1] - c[1])));
  const maskFar = Math.max(...b.outline.map((p) => Math.hypot(p[0] - c[0], p[1] - c[1])));
  assert.ok(Math.abs(maskFar * b.scale - bodyFar) < 1e-6, "the mask is the body, unsqueezed into the ink's own px");
});

test("the ball ink is the marks' own mix, concentrated: the same family, darker", () => {
  const marks = ["#FF8A4C", "#2EE6B0", "#4FB3FF", "#C9CED6"];
  const own = meltMixInk(marks, 1), dense = meltMixInk(marks, 3), core = meltMixInk(marks, 12);
  assert.ok(lum(dense) < lum(own) && lum(core) < lum(dense), `${own} > ${dense} > ${core}`);
  const self = hexToLin(meltMixInk(["#FF8A4C"], 1)), want = hexToLin("#FF8A4C");   // ink.mjs ksFromR clamps R to 0.995
  assert.ok(self.every((v, i) => Math.abs(v - want[i]) < 0.01), "one colour mixed with itself is itself (to the K-M clamp)");
  assert.ok(/^#[0-9a-f]{6}$/.test(meltMixInk([], 2)), "a page with no strokes still has an ink");
  // THE INK is the DOMINANT stroke, never the mix (the mix of the golden page's series lands on green)
  const inkH = hexToLin(meltInkOf(marks, 1)), orange = hexToLin("#FF8A4C");
  assert.ok(inkH.every((v, i) => Math.abs(v - orange[i]) < 0.01), "the ink is the first series' stroke");
  const deep = hexToLin(meltInkOf(marks, MELT.INK_DEEP));
  assert.ok(deep[0] > deep[1] && deep[1] > deep[2] && lum(meltInkOf(marks, MELT.INK_DEEP)) < lum("#FF8A4C"), "the same hue, deeper - not green");
  assert.equal(meltTint("melt", 0), 0);
  assert.ok(Math.abs(meltTint("melt", 1) - MELT.TINT_MELT) < 1e-12 && Math.abs(meltTint("ball", 0) - MELT.TINT_MELT) < 1e-12, "continuous");
  assert.equal(meltTint("ball", 0.5), 1, "the marks are all ink by the ball's middle");
});

// ---- the weight --------------------------------------------------------------------------------------------------
test("the ball has WEIGHT: stopaction's squash on the melt's material, held on 2s, heavier than a card's", () => {
  assert.equal(MELT.MASS, "liquid");
  assert.ok(MASS[MELT.MASS].squash_frames >= 2, "a heavy wet body holds its squash two frames");
  assert.ok(MELT.SQUASH > STOP.IMPACT_SQUASH, "and squashes harder than a card");
  assert.ok(MELT.ARC < STOP.ARC && MELT.SPIN_DEG < STOP.SPIN_DEG, "a heavy ball lifts and tumbles less than a card");
  assert.equal(meltSettle(0), 0, "the contact frame is uncompressed");
  const seen = [];
  for (let f = 0; f < 10; f++) seen.push(meltSettle(f / MELT.FPS));
  assert.ok(Math.max(...seen) === MELT.SQUASH, `the squash reaches its dial: ${seen}`);
  assert.equal(seen[seen.length - 1], 0, "and is released");
});

// ---- the throw ---------------------------------------------------------------------------------------------------
test("the throw: the ball sits in its squash, launches, and leaves the stage; the board goes at the launch", () => {
  const to = { x: 1500, y: 900 }, F = 0.72;
  assert.ok(Math.hypot(meltThrowAt(0, to, F).x, meltThrowAt(0, to, F).y) < 1e-9);
  const z = meltThrowAt(1, to, F);
  assert.ok(Math.abs(z.x - to.x) < 1e-6 && Math.abs(z.y - to.y) < 1e-6);
  const t0 = 4.0, at = (u) => meltState(t0, t0 + u * MELT.S, OPTS(), rnd);
  const rest = at(MELT.BALL_END + 0.02);
  assert.equal(rest.phase, "fly");
  assert.ok(rest.boardUp && Math.hypot(rest.xf.x, rest.xf.y) < 1e-9, "at rest, on the board");
  const rel = meltRelease();
  assert.ok(at(rel - 0.01).boardUp && !at(rel + 0.01).boardUp, "the board is up until the launch");
  const end = at(0.999), cx = end.centre[0] + end.xf.x, cy = end.centre[1] + end.xf.y;
  assert.ok(cx - end.r > SB.x + SB.w || cy - end.r > SB.y + SB.h, `still on stage at (${cx.toFixed(0)}, ${cy.toFixed(0)})`);
  assert.equal(end.drops.length, 0); assert.equal(end.reveal, false);
  assert.equal(meltDrawDelay(meltOpts("melt"), true), rel * MELT.S, "the next chart's clock starts at the launch");
  assert.equal(meltDrawDelay(meltOpts("melt"), false), 0, "a world that is not a page has no clock to hold");
  assert.equal(meltDrawDelay(meltOpts("melt:splash:chart"), true), 0, "a splash's chart arrives built, through the stains");
});

// ---- the splash --------------------------------------------------------------------------------------------------
test("the splatter lands ON the board: every drop along its own ray, monotone, never past its landing", () => {
  const c = [900, 520], ks = [0, 0.2, 0.4, 0.6, 0.8, 1], runs = ks.map((k) => splashDrops(c, RECT, k, rnd));
  for (let i = 0; i < MELT.DROPS; i++) {
    let last = -1;
    for (const drops of runs) { assert.ok(drops[i].d >= last - 1e-9 && drops[i].d <= drops[i].land + 1e-9); last = drops[i].d; }
    const d = runs[ks.length - 1][i];
    assert.ok(Math.abs(d.d - d.land) < 1e-9, "landed at k = 1");
    assert.ok(d.x >= RECT.x && d.x <= RECT.x + RECT.w && d.y >= RECT.y && d.y <= RECT.y + RECT.h, `drop ${i} landed off the board`);
  }
  assert.equal(new Set(runs[3].map((d) => d.a)).size, MELT.DROPS, "no two drops on one ray");
  assert.deepEqual(splashDrops(c, RECT, 0.5, rnd), splashDrops(c, RECT, 0.5, rnd), "seeded");
  const mid = runs[2], land = runs[ks.length - 1];
  assert.ok(mid.every((d, i) => d.tail > land[i].tail), "a drop in flight trails a longer tail than a landed splat");
  assert.equal(splashSats(runs[0]).length, 0, "no satellites before the burst");
  assert.equal(splashSats(land).length, 2 * MELT.DROPS, "two satellites behind every splat");
  const d0 = land[0], sp = meltSplatPath(d0.x, d0.y, d0.r, d0.a + Math.PI, d0.tail, rnd, 500);
  assert.ok(sp.startsWith("M") && sp.endsWith("Z") && sp === meltSplatPath(d0.x, d0.y, d0.r, d0.a + Math.PI, d0.tail, rnd, 500), "a closed, seeded splat");
  const nums = sp.match(/-?\d+(\.\d+)?/g).map(Number), far = [];
  for (let i = 0; i + 1 < nums.length; i += 2) far.push(Math.hypot(nums[i] - d0.x, nums[i + 1] - d0.y));
  assert.ok(Math.max(...far) > d0.r * 2, "its tail reaches past its body");
});

test("the paint: stains grow from the drops and the ball's impact, the board's cover goes to exactly nothing", () => {
  const c = [900, 520], r = MELT.BALL_R * RECT.h, drops = splashDrops(c, RECT, 1, rnd);
  const gs = [0, 0.25, 0.5, 0.75, 0.999, 1], paints = gs.map((g) => splashStains(drops, c, r, RECT, g, rnd));
  for (const p of paints) assert.equal(p.stains.length, MELT.DROPS + 1, "one per drop and one under the impact");
  for (let i = 0; i <= MELT.DROPS; i++) {
    let last = -1;
    for (const p of paints) { assert.ok(p.stains[i].r >= last - 1e-9, `stain ${i} shrank`); last = p.stains[i].r; }
  }
  assert.ok(Math.abs(paints[0].stains[0].r - drops[0].r) < 1e-9, "a stain starts as its drop");
  assert.equal(paints[0].cover, 1); assert.equal(paints[paints.length - 1].cover, 0);
  assert.equal(paints[0].rim, 1); assert.equal(paints[paints.length - 1].rim, 0);
});

test("meltState walks each ending: the board is up and never melts, the ink goes, and gone is gone", () => {
  const t0 = 4.0, at = (u, ending) => meltState(t0, t0 + u * MELT.S, OPTS({ ending }), rnd);
  for (const ending of MELT_ENDINGS) {
    const m = at(0.15, ending);
    assert.equal(m.phase, "melt");
    assert.ok(m.boardUp && m.cover === 1 && !m.reveal, `${ending}: the board is whole through the sag`);
    assert.ok(m.run > 0 && m.inkBlur > 0 && m.path.startsWith("M"), "the marks run under the goo");
    assert.equal(m.body, "", "no ball yet");
    const b = at(0.45, ending);
    assert.ok(b.boardUp && b.cover === 1, `${ending}: the board is whole while the ball forms`);
    const g = at(1.0, ending);
    assert.ok(g.gone && !g.boardUp && g.inkOpacity === 0);
  }
  const s = at(0.62, "splash:chart");
  assert.equal(s.xf, null, "a splash does not travel");
  assert.equal(s.drops.length, MELT.DROPS);
  assert.ok(s.boardUp && !s.reveal, "the burst lands on a whole board");
  const p = at(0.85, "splash:chart");
  assert.ok(p.reveal && p.stains.length === MELT.DROPS + 1 && p.boardUp, "then the board is painted through");
  assert.equal(p.spring, 1, "a chart does not spring");
  assert.notEqual(at(0.85, "splash:plate").spring, 1, "a plate springs as it is painted");
  const sp = []; for (let g = 0; g <= 1.0001; g += 0.02) sp.push(meltSpring(g));
  assert.ok(Math.min(...sp) <= 1 - MELT.SPRING + 1e-9 && Math.max(...sp) > 1.02, `up from small, over its rest: ${Math.min(...sp)} ${Math.max(...sp)}`);
  assert.equal(meltSpring(1), 1, "and settled");
  assert.ok(at(0.999, "splash:plate").cover < 0.05, "and the board's cover is all but gone by the end");
  assert.ok(at(0.62, "splash:chart").dropAlpha === 1 && at(0.95, "splash:chart").dropAlpha < 0.05, "a landed drop soaks into its stain");
  assert.ok(at(0.75, "splash:chart").dropAlpha < 0.5 && at(0.75, "splash:chart").dropScale < 1, "by 075 the splats are receding into the chart, never at full ink over it");
  assert.equal(at(0.75, "splash:plate").dropScale, 1, "the plate's splats keep their size");
});

test("meltState is a pure function of t: the same instant twice is the same object", () => {
  for (const ending of MELT_ENDINGS) {
    for (const u of [0, 0.1, 0.3, 0.45, 0.55, 0.7, 0.85, 0.95, 1.2]) {
      const t = 4.0 + u * MELT.S;
      assert.deepEqual(meltState(4.0, t, OPTS({ ending }), rnd), meltState(4.0, t, OPTS({ ending }), rnd), `${ending} u=${u}`);
    }
  }
});

test("the ball and the ending ride the STEPPED clock - on 2s - and the sag does not", () => {
  const t0 = 4.0, fps = MELT.FPS, ballFrom = t0 + MELT.MELT_END * MELT.S, seen = new Set();
  const frames = Math.round((MELT.BALL_END - MELT.MELT_END) * MELT.S * fps);
  for (let f = 0; f < frames; f++) seen.add(meltState(t0, ballFrom + f / fps, OPTS(), rnd).k.toFixed(9));
  assert.ok(seen.size <= Math.ceil(frames / MELT.HOLD) + 1 && seen.size > 1, `${seen.size} poses over ${frames} frames`);
  const span = (MELT.BALL_END - MELT.MELT_END) * MELT.S, tl = 0.1875;
  assert.ok(Math.abs(meltState(t0, ballFrom + tl, OPTS(), rnd).k - stepped(tl, MELT.HOLD, fps) / span) < 1e-12);
  const ks = [];
  for (let f = 0; f < 6; f++) ks.push(meltState(t0, t0 + f / fps, OPTS(), rnd).k);
  assert.equal(new Set(ks).size, 6, "liquid does not step");
});

// ---- the markup --------------------------------------------------------------------------------------------------
test("the filters: blur under an alpha ramp; the run offsets the marks down; the reveal is white cut by filtered stains", () => {
  const f = meltFilterMarkup("meltf", 0.15);
  assert.ok(f.indexOf("feGaussianBlur") < f.indexOf("feFuncA") && f.includes('slope="' + MELT.EDGE_SLOPE + '"'));
  assert.ok(!f.includes("feColorMatrix"));
  const m = meltMaskMarkup("meltm", "meltf");
  assert.ok(m.includes('<mask id="meltm"') && m.includes('filter="url(#meltf)"'));
  const i = meltInkFilterMarkup("melti");
  assert.equal((i.match(/<feOffset /g) || []).length, MELT.RUN_COPIES);
  assert.ok(i.includes('tableValues="0 0 1 1 1"') && i.indexOf("tableValues") < i.indexOf("feOffset"), "faint pixels are cut BEFORE the run: a wash would ramp into a slab");
  assert.ok(i.indexOf("feMerge") < i.indexOf("feGaussianBlur") && i.indexOf("feGaussianBlur") < i.lastIndexOf("feFuncA"), "merge the run, then the goo");
  const r = meltRevealMarkup("meltr", "melts");
  assert.ok(r.includes('fill="#fff"') && r.includes('filter="url(#melts)"') && r.indexOf("<rect") < r.indexOf("<g "), "white first, the stains over it");
  const st = { centre: [100, 200], xf: { x: 10, y: 20, rot: 3 }, squash: { a: 0.3, theta: 0 } };
  assert.ok(/^translate\(110\.00 220\.00\) rotate\(3\.00\) matrix\(1\.3000 0\.0000 0\.0000 0\.7692 0 0\) translate\(-100\.00 -200\.00\)$/.test(meltBodyTransform(st)), meltBodyTransform(st));
});

// ---- THE WEIGHT PHASE (R26-118 / E88 s6-s7) ------------------------------------------------------------------------
// The operator, 2026-09-14: *"we need to make sure our ball has real density, and we should probably roll it around or
// manipulate it a bit for good measure to show that it has real mass & gravity"*. It is OPT-IN, so the first thing
// these pin is that a melt which never said `weight` is the melt that shipped - phase for phase, share for share.
const W = { weight: true, wmass: "metal", secs: MELT.S + MELT.W_S };

test("the weight phase is opt-in: without it every phase, share and release is what it was", () => {
  assert.equal(meltWeightShare(MELT.S), 0);
  assert.equal(meltOpts("melt").weight, false);
  assert.equal(meltPhase(MELT.MELT_END).name, "ball");
  assert.equal(meltPhase(MELT.BALL_END).name, "fly");
  assert.equal(meltRelease(), MELT.BALL_END + MELT.ANTIC * (1 - MELT.BALL_END));
  assert.deepEqual(meltBallRing([0, 0], 10, {}), ballCircle([0, 0], 10, MELT.CIRCLE_N), "no weight, no living ring");
});

test("`melt:weight` parses, names its material, lengthens its own default window and refuses a stranger", () => {
  const o = meltOpts("melt:weight");
  assert.equal(o.weight, true);
  assert.equal(o.wmass, "metal", "E88 s7: the ball is METAL by default");
  assert.equal(o.secs, MELT.S + MELT.W_S, "the four beats need their own seconds");
  for (const mat of MELT_MATERIALS) assert.equal(meltOpts("melt:weight:" + mat).wmass, mat);
  assert.equal(meltOpts("melt:weight:2.8").secs, 2.8, "a declared length is the whole window");
  assert.equal(meltOpts("melt:splash:plate:weight:ink").ending, "splash:plate");
  assert.throws(() => meltOpts("melt:weight:bronze"), /bronze is not a material/);
  assert.equal(meltWeightMass({ weight: true, wmass: "bronze" }), MELT.W_MASS, "an unknown material is never painted");
});

test("with weight the other three phases keep their shares of what is LEFT, and the weight takes W_S seconds", () => {
  const secs = MELT.S + MELT.W_S, w = meltWeightShare(secs, W);
  assert.ok(Math.abs(w * secs - MELT.W_S) < 1e-12);
  const sh = meltShares(Object.assign({ secs }, W));
  assert.ok(Math.abs(sh.reduce((a, b) => a + b, 0) - 1) < 1e-12);
  assert.ok(Math.abs(sh[0] / sh[1] - MELT.MELT_END / (MELT.BALL_END - MELT.MELT_END)) < 1e-12, "melt : ball is untouched");
  const P = Object.assign({ secs }, W);
  assert.equal(meltPhase(MELT.MELT_END * (1 - w) + 1e-9, P).name, "ball");
  assert.equal(meltPhase(MELT.BALL_END * (1 - w) + 1e-9, P).name, "weight");
  assert.equal(meltPhase(MELT.BALL_END * (1 - w) + w + 1e-9, P).name, "fly");
  assert.ok(meltRelease(P) > MELT.BALL_END * (1 - w) + w, "the board stays up until the ball is thrown");
  // and W_MAX caps it: a short melt:weight cannot be all weight
  assert.ok(Math.abs(meltWeightShare(1.0, W) - MELT.W_MAX) < 1e-12);
});

test("the roll does not slip: the turn angle is the distance over the radius, at every u", () => {
  const r = 50, span = MELT.W_S;
  for (const u of [0.3, 0.45, 0.62, 0.9]) {
    const w = meltWeightAt(u * span, span, r, Object.assign({ dir: 1 }, W));
    assert.ok(Math.abs(w.turn - w.x / r) < 1e-12, `u ${u}: ${w.turn} vs ${w.x / r}`);
  }
  const left = meltWeightAt(0.45 * span, span, r, Object.assign({ dir: -1 }, W));
  const right = meltWeightAt(0.45 * span, span, r, Object.assign({ dir: 1 }, W));
  assert.ok(Math.abs(left.x + right.x) < 1e-12 && Math.abs(left.turn + right.turn) < 1e-12, "the other way turns the other way");
});

test("the friction stops the roll at the authored distance, inside its own beat", () => {
  const r = 50, span = MELT.W_S, beat = (MELT.W_ROLL - MELT.W_LAND) * span;
  const roll = rollXf(MELT.W_ROLL_PX, r, MELT.W_ROLL_FRICTION, beat);
  assert.ok(roll.T < beat, `the roll's own T (${roll.T}) has to land inside its beat (${beat})`);
  assert.ok(Math.abs(roll.s - MELT.W_ROLL_PX) < 1e-9, "it stops where the math says");
  const end = meltWeightAt(MELT.W_ROLL * span - 1e-6, span, r, Object.assign({ dir: 1 }, W));
  assert.ok(Math.abs(end.x - MELT.W_ROLL_PX) < 1e-6, `the beat ends at the authored travel: ${end.x}`);
  // the NUDGE adds its own, and it is sold BEFORE it moves: the ball leans BACK first (48 s48.6)
  const lean = meltWeightAt((MELT.W_ROLL * span) + MELT.W_ANTIC_S / 2, span, r, Object.assign({ dir: 1 }, W));
  assert.ok(lean.x < MELT.W_ROLL_PX, `the anticipation leans back: ${lean.x}`);
  const rest = meltWeightAt(span, span, r, Object.assign({ dir: 1 }, W));
  assert.ok(Math.abs(rest.x - (MELT.W_ROLL_PX + MELT.W_NUDGE_PX)) < 1e-6, `it settles at roll + nudge: ${rest.x}`);
  assert.equal(rest.beat, "settle");
});

test("the four beats in order, and the contact shadow tightens as it falls and then rides a frame behind", () => {
  const r = 50, span = MELT.W_S, at = (k) => meltWeightAt(k * span, span, r, Object.assign({ dir: 1 }, W));
  assert.equal(at(0).beat, "fall");
  assert.equal(at(MELT.W_LAND + 0.05).beat, "roll");
  assert.equal(at(MELT.W_ROLL + 0.05).beat, "nudge");
  assert.equal(at(MELT.W_SETTLE + 0.05).beat, "settle");
  const high = at(0), low = at(MELT.W_LAND * 0.98);
  assert.ok(high.h > low.h && low.y < 0, "it is still coming down");
  assert.ok(low.shadow.scale > high.shadow.scale && low.shadow.blur < high.shadow.blur, "FAR to NEAR as it nears");
  // the shadow is LAG_FRAMES behind the ball while it rolls (HF-2)
  const mid = at(0.35);
  assert.ok(mid.shadowX < mid.x && mid.x - mid.shadowX > 1, `the shadow lags: ${mid.shadowX} vs ${mid.x}`);
  const back = meltWeightAt(0.35 * span - STOP.LAG_FRAMES / MELT.FPS, span, r, Object.assign({ dir: 1 }, W));
  assert.ok(Math.abs(mid.shadowX - back.x) < 1e-9, "and it is exactly where the ball was a frame ago");
});

test("METAL is a dead stop: no squash, no rebound - the roll and the nudge carry the weight (E88 s7)", () => {
  const r = 50, span = MELT.W_S, ts = MELT.W_LAND * span + 1 / MELT.FPS;
  assert.equal(MASS.metal.squash_frames, 0);
  const metal = meltWeightAt(ts, span, r, Object.assign({ dir: 1 }, W));
  assert.equal(metal.squash.a, 0, "a rigid dense thing does not squash");
  const ink = meltWeightAt(ts, span, r, Object.assign({ dir: 1 }, W, { wmass: "ink" }));
  assert.ok(ink.squash.a > 0, "ink does");
  assert.ok(metal.kick.length >= 1 && metal.kick[0].a[0] > 0, "the landing re-excites the drop's modes instead");
});

test("the ball is a LIVING ring under weight: its area is the circle's, and it is not the circle", () => {
  const ring = meltBallRing([0, 0], 40, Object.assign({ te: 0.04, excite: [{ at: 0, a: DROP.A }] }, W));
  assert.equal(ring.length, MELT.CIRCLE_N, "the morph's resample still lands ON the vertices");
  assert.ok(Math.abs(dropArea(ring) / (Math.PI * 40 * 40) - 1) < 1e-6, "incompressible");
  const rs = ring.map((p) => Math.hypot(p[0], p[1]));
  assert.ok(Math.max(...rs) - Math.min(...rs) > 0.03 * 40, "it is wriggling to contain itself, not a circle");
});

test("the mark turns with the ball - that is what makes the roll a roll and not a slide", () => {
  const c = [100, 100], r = 50;
  const a = meltMarkAt(c, r, 0), b = meltMarkAt(c, r, Math.PI / 2);
  assert.ok(Math.abs(Math.hypot(a.x - c[0], a.y - c[1]) - r * MELT.W_MARK_AT) < 1e-9, "it sits on the face, not the rim");
  assert.ok(Math.hypot(a.x - b.x, a.y - b.y) > 0.5 * r, "a quarter turn moves it a long way");
  assert.ok(Math.abs((b.deg - a.deg) - 90) < 1e-9, "and its streak turns with it");
  assert.ok(a.rx > a.ry, "a streak, not a dot");
});

test("which way it rolls is the ending's own direction", () => {
  const rect = { x: 0, y: 0, w: 400, h: 300 }, sb = { x: -20, y: -15, w: 440, h: 330 };
  assert.equal(meltRollDir([100, 100], rect, { ending: "throw", to: [1.02, 1.32], stagebox: sb }), 1, "toward the exit");
  assert.equal(meltRollDir([100, 100], rect, { ending: "throw", to: [-0.2, 1.3], stagebox: sb }), -1);
  assert.equal(meltRollDir([300, 100], rect, { ending: "splash:chart", stagebox: sb }), -1, "toward the board's middle");
});

test("the weight phase is a pure function of t: two calls at one u are identical", () => {
  const rect = { x: 40, y: 30, w: 520, h: 360 }, o = Object.assign({ rect, ending: "throw" }, W);
  for (const u of [0.40, 0.55, 0.70, 0.86, 0.95]) {
    const t = 3 + u * o.secs;
    const a = meltState(3, t, o, rnd), b = meltState(3, t, o, rnd);
    assert.deepEqual(a, b, `u ${u}`);
  }
  const mid = meltState(3, 3 + 0.62 * o.secs, o, rnd);
  assert.equal(mid.phase, "weight");
  assert.ok(mid.mark && mid.hl && mid.shadow, "the mark, the highlight and the contact shadow are all on it");
  assert.ok(mid.body.startsWith("M"), "and it paints a path");
  const land = meltState(3, 3 + (MELT.BALL_END * (1 - meltWeightShare(o.secs, o))) * o.secs + 0.001, o, rnd);
  assert.equal(land.phase, "weight");
  assert.equal(land.weight, "fall", "the phase opens with the last of its height");
  const fly = meltState(3, 3 + 0.99 * o.secs, o, rnd);
  assert.equal(fly.phase, "fly");
  assert.ok(Math.abs(fly.turn - (MELT.W_ROLL_PX + MELT.W_NUDGE_PX) / fly.r) < 1e-6, "the ending keeps the turn the roll left");
});
