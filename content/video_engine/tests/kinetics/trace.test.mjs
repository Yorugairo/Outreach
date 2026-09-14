// P57 T18 / R26-95 - THE TRACE PROMOTED (the P55 T7 recipe). The promotion's proof is that every golden is
// byte-identical, so what this file pins is that the module still carries the INLINE ENGINE's numbers and
// arithmetic: the dials are the literals `paintSpecies sp.kind === "trace"` carried (SP.TRACE_PERIOD 3.2,
// SP.TRACE_DRAW 1.1 and the branch's own), the plain trace is the same seeded zigzag on the same period, the
// hop is the same quadratic bow, and the arrowhead lands on the same law for both. What may be DECLARED on a
// hop is the compiler's (build_scene_timeline_f.py:1344); the painter carries no opinion about it, and this
// file checks that it does not start to.
import { test } from "node:test";
import assert from "node:assert/strict";
import { TRACE, traceHopOf, tracePhase, traceDrawK, traceHopPoints, tracePlainPoints, tracePathD,
         traceWidth, traceOpacity, traceHead, traceStroke, paintTrace } from "../../scripts/species/trace.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const clamp = (v) => Math.min(1, Math.max(0, v));      // the engine's clamp01, verbatim
const FLAT = () => 0.5;                                // the hash at its middle: no jog at all
const STAGE = [1920, 1080];                            // the engine's STAGE_W / STAGE_H
const BOX = { x: 400, y: 300, w: 800, h: 400 };        // a declared region resolves to a box in stage px
const hop = (o = {}) => Object.assign({ from: [0.2, 0.6], to: [0.8, 0.3] }, o);
const nums = (d) => (d.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
// a point's signed distance from the chord, along the normal the painter bows toward
const offChord = (p, a, b) => {
  const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy);
  return ((p[0] - a[0]) * -dy + (p[1] - a[1]) * dx) / L;
};

// ---------------------------------------------------------------- the dials, as the inline code carried them
test("every dial is the inline engine's literal, to the digit, and frozen", () => {
  assert.ok(Object.isFrozen(TRACE));
  assert.equal(TRACE.PERIOD, 3.2, "SP.TRACE_PERIOD");
  assert.equal(TRACE.DRAW_S, 1.1, "SP.TRACE_DRAW");
  assert.equal(TRACE.N, 7, "the branch's `const n = 7` - one sampling for both forms");
  assert.equal(TRACE.MIN_DRAW_S, 0.05, "Math.max(0.05, +hop.draw_s || SP.TRACE_DRAW)");
  assert.deepEqual([TRACE.BOW, TRACE.BOW_K], [0.18, 2]);
  assert.deepEqual([TRACE.JAG_K, TRACE.HASH_SALT], [0.35, 44]);
  assert.deepEqual([TRACE.X0, TRACE.X_SPAN, TRACE.Y0, TRACE.Y_SPAN], [0.08, 0.84, 0.12, 0.76]);
  assert.deepEqual([TRACE.WIDTH, TRACE.WIDTH_K, TRACE.WIDTH_MIN], [7, 0.045, 3]);
  assert.deepEqual([TRACE.FADE_AT, TRACE.FADE_SPAN, TRACE.IN_S], [0.82, 0.18, 0.4]);
  assert.deepEqual([TRACE.HEAD_K, TRACE.HEAD_MIN, TRACE.HEAD_W, TRACE.HEAD_A], [3, 8, 0.12, 0.5]);
  assert.equal(TRACE.COLOR, "#B0201F");
  assert.ok(near(TRACE.FADE_AT + TRACE.FADE_SPAN, 1), "the hold and the fade are the whole period");
  assert.ok(TRACE.X0 + TRACE.X_SPAN < 1 && TRACE.Y0 + TRACE.Y_SPAN < 1, "the zigzag is inset at both ends");
});

test("a hop needs BOTH ends, and what else may be declared on it is the compiler's", () => {
  assert.equal(traceHopOf({ kind: "trace" }), null);
  assert.equal(traceHopOf({ hop: { from: [0, 0] } }), null, "one end is not a crossing");
  assert.equal(traceHopOf({ hop: { to: [1, 1] } }), null);
  assert.deepEqual(traceHopOf({ hop: hop() }), hop());
  const src = paintTrace.toString() + traceHopPoints.toString() + traceWidth.toString();
  assert.ok(!/errs|throw|reject/i.test(src), "the declaration is validated at build time, never softened here");
});

// ---------------------------------------------------------------- the period: a pure function of t
test("the plain trace's phase is its own period from `at`, and a hop has none", () => {
  assert.ok(near(tracePhase(10, 10, null), 0));
  assert.ok(near(tracePhase(10 + TRACE.PERIOD / 2, 10, null), 0.5));
  const circ = (a, b) => Math.min(Math.abs(a - b), 1 - Math.abs(a - b));   // the phase is a circle, and 1 is 0
  assert.ok(circ(tracePhase(10 + TRACE.PERIOD, 10, null), 0) < 1e-12, "it goes again every PERIOD");
  assert.ok(circ(tracePhase(10 + TRACE.PERIOD * 2.25, 10, null), 0.25) < 1e-12, "... and again, off the same t");
  assert.ok(near(tracePhase(9.6, 10, null), 0.875), "before `at` it still lands in [0, 1) - never negative");
  assert.equal(tracePhase(12.7, 10, hop()), 0, "a hop is drawn ONCE and held: it has no period at all");
});

test("the draw fraction: the trace's over the period's share, the hop's over its own declared seconds", () => {
  assert.ok(near(traceDrawK(10, 10, null, tracePhase(10, 10, null), clamp), 0));
  const half = 10 + TRACE.DRAW_S / 2;
  assert.ok(near(traceDrawK(half, 10, null, tracePhase(half, 10, null), clamp), 0.5), "DRAW_S is the draw");
  const held = 10 + TRACE.DRAW_S + 0.3;
  assert.equal(traceDrawK(held, 10, null, tracePhase(held, 10, null), clamp), 1, "then it HOLDS at 1");
  const h = hop({ draw_s: 0.55 });
  assert.ok(near(traceDrawK(10.22, 10, h, 0, clamp), 0.4));
  assert.equal(traceDrawK(20, 10, h, 0, clamp), 1, "and stays landed to the end of dur");
  assert.equal(traceDrawK(10, 10, h, 0, clamp), 0);
  assert.ok(near(traceDrawK(10.55, 10, hop(), 0, clamp), 0.5), "no draw_s declared: the dial, 1.1 s");
  assert.ok(near(traceDrawK(10.55, 10, hop({ draw_s: 0 }), 0, clamp), 0.5), "a draw_s of 0 is no draw_s: the dial");
  assert.equal(traceDrawK(10.05, 10, hop({ draw_s: 0.01 }), 0, clamp), 1, "a tiny one floors at MIN_DRAW_S ...");
  assert.ok(near(traceDrawK(10.025, 10, hop({ draw_s: 0.01 }), 0, clamp), 0.5), "... so nothing divides by ~0");
});

// ---------------------------------------------------------------- the hop's bow
test("the hop is a quadratic bow: it leaves one named point and LANDS on the other", () => {
  const pts = traceHopPoints(hop({ bow: 0.16 }), ...STAGE);
  assert.equal(pts.length, TRACE.N + 1);
  assert.ok(near(pts[0][0], 0.2 * 1920) && near(pts[0][1], 0.6 * 1080), "from, as a stage fraction");
  assert.ok(near(pts[TRACE.N][0], 0.8 * 1920) && near(pts[TRACE.N][1], 0.3 * 1080), "to, the same way");
});

test("the belly is 4uv x bow x the chord's own length - a curve passes at HALF its control's offset", () => {
  const bow = 0.16, pts = traceHopPoints(hop({ bow }), ...STAGE);
  const a = pts[0], b = pts[TRACE.N], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
  for (let i = 0; i <= TRACE.N; i++) {
    const u = i / TRACE.N, v = 1 - u;
    assert.ok(near(offChord(pts[i], a, b), 4 * u * v * bow * L, 1e-9), `point ${i} rides its own share of the bow`);
  }
  assert.ok(near(4 * 0.5 * 0.5 * bow * L, bow * L), "... which is exactly bow x L at the middle");
});

test("the bow's SIGN is the side it passes on, and the two sides mirror about the chord", () => {
  const up = traceHopPoints(hop({ bow: 0.2 }), ...STAGE), down = traceHopPoints(hop({ bow: -0.2 }), ...STAGE);
  const flat = traceHopPoints(hop({ bow: 0 }), ...STAGE);
  for (let i = 0; i <= TRACE.N; i++) {
    assert.ok(near(up[i][0] + down[i][0], 2 * flat[i][0], 1e-9), "x mirrors about the chord");
    assert.ok(near(up[i][1] + down[i][1], 2 * flat[i][1], 1e-9), "... and so does y");
  }
  assert.ok(offChord(up[3], up[0], up[TRACE.N]) > 0 && offChord(down[3], down[0], down[TRACE.N]) < 0);
  assert.deepEqual(traceHopPoints(hop(), ...STAGE), traceHopPoints(hop({ bow: TRACE.BOW }), ...STAGE),
                   "no bow declared = the dial, 0.18");
  assert.deepEqual(traceHopPoints(hop({ bow: "x" }), ...STAGE), traceHopPoints(hop(), ...STAGE),
                   "... and so is a bow that is not a number");
});

test("a hop of no length does not divide by zero", () => {
  const pts = traceHopPoints({ from: [0.5, 0.5], to: [0.5, 0.5] }, ...STAGE);
  assert.ok(pts.every(([x, y]) => Number.isFinite(x) && Number.isFinite(y)), "|| 1 is why");
});

// ---------------------------------------------------------------- the plain trace's seeded zigzag
test("the zigzag runs the box's own diagonal, inset, with only its INTERIOR points jogged", () => {
  const pts = tracePlainPoints(BOX, 7, FLAT);
  assert.equal(pts.length, TRACE.N + 1);
  assert.deepEqual(pts[0], [BOX.x + BOX.w * TRACE.X0, BOX.y + BOX.h * TRACE.Y0]);
  assert.deepEqual(pts[TRACE.N], [BOX.x + BOX.w * (TRACE.X0 + TRACE.X_SPAN), BOX.y + BOX.h * (TRACE.Y0 + TRACE.Y_SPAN)]);
  assert.ok(pts.every(([x], i) => i === 0 || x > pts[i - 1][0]), "x only ever runs forward: a route, not a scribble");
  const jagged = tracePlainPoints(BOX, 7, (s, i, salt) => (salt === TRACE.HASH_SALT ? 1 : 0));
  assert.deepEqual(jagged[0], pts[0], "the first point never jogs ...");
  assert.deepEqual(jagged[TRACE.N], pts[TRACE.N], "... and neither does the last");
  assert.ok(near(jagged[1][1] - pts[1][1], 0.5 * BOX.h * TRACE.JAG_K), "an interior point jogs by half of JAG_K x h");
  assert.ok(near(jagged[1][0], pts[1][0]), "and only in y");
});

test("the jitter's one source is the seeded hash - never Math.random (the still-life law)", () => {
  assert.ok(!/Math\s*\.\s*random/.test(tracePlainPoints.toString() + paintTrace.toString()));
  const h = (s, i) => ((s * 31 + i * 17) % 100) / 100;
  assert.deepEqual(tracePlainPoints(BOX, 11, h), tracePlainPoints(BOX, 11, h),
                   "the same seed draws the same zigzag: a cold seek lands where a play does");
  assert.notDeepEqual(tracePlainPoints(BOX, 11, h), tracePlainPoints(BOX, 12, h), "... a different seed does not");
});

// ---------------------------------------------------------------- the path, the width, the opacity, the head
test("the path is one polyline in stage px, to a tenth", () => {
  assert.equal(tracePathD([[1, 2], [3.456, 4]]), "M1.0 2.0 L3.5 4.0");
  assert.equal(tracePathD(traceHopPoints(hop(), ...STAGE)).split("L").length - 1, TRACE.N, "N chords, N + 1 points");
});

test("the stroke: the hop's declared width, or the box's, floored - and the row's colour or the ledger's red", () => {
  assert.equal(traceWidth(hop({ width: 9 }), BOX), 9);
  assert.equal(traceWidth(hop(), BOX), TRACE.WIDTH, "a hop with no width takes the dial");
  assert.ok(near(traceWidth(null, BOX), BOX.w * TRACE.WIDTH_K));
  assert.equal(traceWidth(null, { x: 0, y: 0, w: 40, h: 40 }), TRACE.WIDTH_MIN, "a small region still reads");
  assert.equal(traceStroke({ kind: "trace" }, 9).stroke, TRACE.COLOR);
  assert.equal(traceStroke({ color: "#25313C" }, 9).stroke, "#25313C");
  assert.equal(traceStroke({}, 7.26)["stroke-width"], "7.3");
  assert.equal(traceStroke({}, 9).fill, "none");
});

test("the plain trace fades at the end of its period; a hop is HELD", () => {
  const k = (t, dur, at = 10) => (t - at) / dur;
  const t1 = 10 + TRACE.PERIOD * 0.5;
  assert.ok(near(traceOpacity(tracePhase(t1, 10, null), k(t1, 12), 12, null, clamp), 1), "mid-period: full");
  const t2 = 10 + TRACE.PERIOD * 0.91;      // half way through the fade
  assert.ok(near(traceOpacity(tracePhase(t2, 10, null), k(t2, 12), 12, null, clamp), 0.5), "then out over FADE_SPAN");
  assert.ok(near(traceOpacity(0, 0.5, 12, hop(), clamp), 1), "a hop does not fade at all ...");
  assert.ok(near(traceOpacity(0, 1, 12, hop(), clamp), 1), "... not even on the last frame of dur");
  assert.ok(near(traceOpacity(0, 1, 12, null, clamp), 0), "where the plain trace goes out with the species");
  assert.ok(near(traceOpacity(0, TRACE.IN_S / 2 / 12, 12, hop(), clamp), 0.5), "both fade IN over IN_S");
});

test("the arrowhead lands on the last segment's own angle, both forms", () => {
  const pts = [[0, 0], [10, 0], [20, 0], [30, 0], [40, 0], [50, 0], [60, 0], [100, 0]];   // N + 1, running +x
  const [bx, by, tipx, tipy, cx] = nums(traceHead(pts, 9, hop(), BOX));
  assert.ok(near(tipx, 100) && near(tipy, 0), "the two barbs meet AT the point the line landed on");
  const back = 9 * TRACE.HEAD_K;
  assert.ok(near(bx, +(100 - back * Math.cos(-TRACE.HEAD_A)).toFixed(1)), "HEAD_K stroke widths back, on a hop");
  assert.ok(near(by, +(0 - back * Math.sin(-TRACE.HEAD_A)).toFixed(1)), "... at HEAD_A off the angle");
  assert.ok(near(cx, bx), "the second barb is the first mirrored: the angle is signed, the reach is not");
  assert.ok(near(nums(traceHead(pts, 4, null, BOX))[0], +(100 - BOX.w * TRACE.HEAD_W * Math.cos(-TRACE.HEAD_A)).toFixed(1)),
            "a plain trace reaches back HEAD_W of the box's width");
  assert.ok(near(nums(traceHead(pts, 4, null, { x: 0, y: 0, w: 40, h: 40 }))[0],
                 +(100 - TRACE.HEAD_MIN * Math.cos(-TRACE.HEAD_A)).toFixed(1)), "... floored at HEAD_MIN");
});

// ---------------------------------------------------------------- the painter, over a stub DOM
const stub = () => {
  const made = [], drawn = [];
  const el = (tag, cls, parent, attrs) => {
    const node = { tag, cls, parent, attrs: Object.assign({}, attrs),
                   setAttribute(k, v) { this.attrs[k] = v; }, getAttribute(k) { return this.attrs[k]; } };
    made.push(node);
    return node;
  };
  return { made, drawn, el, drawOn: (node, f) => drawn.push([node, f]) };
};

const ctxFor = (sp, t, s) => ({
  sp, t, k: (t - sp.at) / (sp.dur || 1), dur: sp.dur || 1, seed: 7, svg: "spSvg", el: s.el,
  resolveTarget: () => BOX, drawOn: s.drawOn, clamp, hash: FLAT, STAGE_W: STAGE[0], STAGE_H: STAGE[1],
});

test("no resolved target, nothing painted (the targeting law)", () => {
  const s = stub();
  paintTrace(Object.assign(ctxFor({ kind: "trace", at: 10, dur: 6 }, 11, s), { resolveTarget: () => null }));
  assert.deepEqual([s.made.length, s.drawn.length], [0, 0]);
});

test("mid-draw: one path, drawn part way, no head yet - the instant the `trace-hop` golden pins", () => {
  const s = stub();
  paintTrace(ctxFor({ kind: "trace", at: 8.0, dur: 9.0, color: "#B0201F",
                      hop: hop({ bow: -0.2, draw_s: 0.9, width: 7 }) }, 8.54, s));
  assert.equal(s.made.length, 1, "the line only: the head lands when the line does");
  assert.ok(near(s.drawn[0][1], 0.6, 1e-12), "0.54 s into a 0.9 s draw");
  assert.equal(s.made[0].attrs.opacity, "1.000", "a hop is in by IN_S and held from there");
  assert.equal(s.made[0].attrs["stroke-width"], "7.0");
  assert.equal(s.made[0].attrs.stroke, "#B0201F");
});

test("landed: the head is painted, on the line's own opacity and stroke", () => {
  const s = stub();
  paintTrace(ctxFor({ kind: "trace", at: 5.0, dur: 12.0, hop: hop({ draw_s: 0.55, width: 9 }) }, 8.54, s));
  assert.equal(s.made.length, 2, "the line and its arrowhead");
  const [line, head] = s.made;
  assert.equal(head.attrs.opacity, line.attrs.opacity, "the two arrive and leave as one mark");
  assert.equal(head.attrs.stroke, line.attrs.stroke);
  assert.equal(head.attrs["stroke-width"], line.attrs["stroke-width"]);
  assert.equal(head.attrs.fill, "none");
  assert.equal(s.drawn.length, 1, "the head is never dashed on - it lands whole");
  assert.ok(head.attrs.d.startsWith("M"));
});

test("the plain trace redraws on its own period, and the head goes with it", () => {
  const sp = { kind: "trace", at: 5.0, dur: 12.0, color: "#25313C" };
  const mid = stub();
  paintTrace(ctxFor(sp, 8.54, mid));                       // 1.106 periods in: 0.309 through the draw
  assert.ok(near(mid.drawn[0][1], ((8.54 - 5) / TRACE.PERIOD % 1) * TRACE.PERIOD / TRACE.DRAW_S, 1e-12));
  assert.equal(mid.made.length, 1, "mid-draw, so no head");
  const held = stub();
  paintTrace(ctxFor(sp, 5 + TRACE.DRAW_S + 0.2, held));
  assert.equal(held.made.length, 2, "drawn and holding: the head is up");
  const again = stub();
  paintTrace(ctxFor(sp, 8.54 + TRACE.PERIOD, again));
  assert.deepEqual(again.made[0].attrs, mid.made[0].attrs, "one period later it is the SAME picture");
});
