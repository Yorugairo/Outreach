// P48 T2 - the chart-transition interpolators: exact at both ends, linear between, fades that respect the domain.
import { test } from "node:test";
import assert from "node:assert/strict";
import { xfLerp, xfPoint, xfPath, xfFade, xfInside, xfRect, XF,
         xfSpanTop, xfStripRing, xfBarRing, xfRingPath, xfRemakeClock, xfRemakeTravel, REMAKE, REMAKE_BEAT } from "../../scripts/kinetics/chartxf.mjs";
import { morphAPrepare, morphAAt } from "../../scripts/kinetics/morph_a.mjs";

const mapA = (x, v) => [100 + x * 10, 400 - v * 2];       // scale A: 10 px per x, 2 px per unit
const mapB = (x, v) => [100 + (x - 5) * 20, 400 - v * 4]; // scale B: a window from x=5, twice the y magnification

test("xfLerp is exact at the ends and clamps outside the clock", () => {
  assert.equal(xfLerp(3, 7, 0), 3); assert.equal(xfLerp(3, 7, 1), 7);
  assert.equal(xfLerp(3, 7, -1), 3); assert.equal(xfLerp(3, 7, 2), 7);
  assert.equal(xfLerp(3, 7, 0.25), 4);
});

test("xfPoint moves a datum from its place under A to its place under B, and never changes the datum", () => {
  assert.deepEqual(xfPoint(7, 50, mapA, mapB, 0), mapA(7, 50));
  assert.deepEqual(xfPoint(7, 50, mapA, mapB, 1), mapB(7, 50));
  const mid = xfPoint(7, 50, mapA, mapB, 0.5);
  assert.equal(mid[0], (mapA(7, 50)[0] + mapB(7, 50)[0]) / 2);
  assert.equal(mid[1], (mapA(7, 50)[1] + mapB(7, 50)[1]) / 2);
});

test("xfPath writes an SVG d that starts with M and lands exactly on B at u=1", () => {
  const pts = [[0, 10], [5, 20], [10, 30]];
  const end = xfPath(pts, mapA, mapB, 1);
  assert.deepEqual(end.pts, pts.map(([x, v]) => mapB(x, v)));
  assert.match(end.d, /^M[-\d.]+ [-\d.]+ L/);
  assert.equal(xfPath(pts, mapA, mapB, 0).d, pts.map(([x, v], k) => (k ? "L" : "M") + mapA(x, v)[0].toFixed(1) + " " + mapA(x, v)[1].toFixed(1)).join(" "));
});

test("xfFade: a mark inside the target holds, a leaving one is gone by LEAVE, an arriving one is absent until ARRIVE", () => {
  assert.equal(xfFade(true, false, 0.3), 1);
  assert.equal(xfFade(false, false, 0), 1);
  assert.equal(xfFade(false, false, XF.LEAVE), 0);
  assert.equal(xfFade(false, false, 1), 0);
  assert.equal(xfFade(true, true, 0), 0);
  assert.equal(xfFade(true, true, 1 - XF.ARRIVE), 0);
  assert.equal(xfFade(true, true, 1), 1);
  assert.equal(xfFade(false, true, 0.9), 0, "a mark arriving outside its own domain never shows");
});

test("xfInside takes the domain in either order and keeps the tick on the edge", () => {
  assert.ok(xfInside(5, 0, 10)); assert.ok(xfInside(5, 10, 0));
  assert.ok(xfInside(10, 0, 10)); assert.ok(!xfInside(10.01, 0, 10));
});

test("xfRect lerps every edge", () => {
  const r = xfRect({ x: 0, y: 0, w: 10, h: 10 }, { x: 10, y: 20, w: 30, h: 50 }, 0.5);
  assert.deepEqual(r, { x: 5, y: 10, w: 20, h: 30 });
});

// ---- P61 T2 - THE WHOLE-CHART REMAKE: the ring both forms are described by, and its one clock ----
// A datum's share of the area under a line and a bar's rectangle are built column by column, in ONE
// order, so morph_a's existing pairing rule (resample: false, normalise: false) corresponds them with
// offset 0 - the remake invents no second pairing law.

test("xfSpanTop samples the line's own y between two x, exactly at the ends", () => {
  const pts = [[0, 100], [10, 0], [20, 50]];
  const top = xfSpanTop(pts, 5, 15, 5);
  assert.equal(top.length, 5);
  assert.deepEqual(top[0], [5, 50]);               // half way down the first leg
  assert.deepEqual(top[top.length - 1], [15, 25]); // half way up the second
  assert.ok(top.every(([x], i, a) => i === 0 || x > a[i - 1][0]), "x is increasing");
});

test("xfSpanTop holds the polyline's own end value outside it and never invents a point", () => {
  const pts = [[0, 100], [10, 0]];
  assert.deepEqual(xfSpanTop(pts, -5, 5, 3)[0], [-5, 100], "before the first datum the line's first y holds");
  assert.deepEqual(xfSpanTop(pts, 5, 15, 3)[2], [15, 0], "past the last datum the line's last y holds");
});

test("xfStripRing closes the ring top-left to right, bottom right to left", () => {
  const ring = xfStripRing([[0, 10], [5, 10]], [[0, 90], [5, 90]]);
  assert.deepEqual(ring, [[0, 10], [5, 10], [5, 90], [0, 90]]);
});

test("xfBarRing describes a bar as the SAME ring: n along its value edge, n along its base", () => {
  const ring = xfBarRing({ x: 100, y: 40, w: 60, h: 160, base: 200 }, 4);
  assert.equal(ring.length, 8);
  assert.deepEqual(ring[0], [100, 40]);
  assert.deepEqual(ring[3], [160, 40]);
  assert.deepEqual(ring[4], [160, 200]);
  assert.deepEqual(ring[7], [100, 200]);
  const neg = xfBarRing({ x: 0, y: 200, w: 10, h: 30, base: 200, neg: true }, 2);
  assert.deepEqual(neg[0], [0, 230], "a negative bar's VALUE edge is the one below its base");
  assert.deepEqual(neg[3], [0, 200]);
});

test("a column ring and a bar ring correspond under morph_a with offset 0, and the lerp is exact at both ends", () => {
  const n = 8;
  const pts = [[0, 300], [50, 120], [100, 180], [150, 60]];
  const top = xfSpanTop(pts, 50, 100, n);
  const A = xfStripRing(top, top.map(([x]) => [x, 400]));
  const B = xfBarRing({ x: 220, y: 150, w: 40, h: 250, base: 400 }, n);
  assert.equal(A.length, B.length);
  const prep = morphAPrepare(A, B, { resample: false, normalise: false });
  assert.equal(prep.offset, 0, "the two descriptions correspond column for column - morph_a's own check");
  assert.deepEqual(morphAAt(prep, 0).outline, A);
  const end = morphAAt(prep, 1).outline;   // a + (b - a) * 1 is b to 1e-13, not bit for bit: the PAINTER pins the
  assert.ok(end.every((q, i) => Math.abs(q[0] - B[i][0]) < 1e-9 && Math.abs(q[1] - B[i][1]) < 1e-9));  // ends to A and B themselves (lpPaintMorphTo's own u <= 0 / u >= 1 branch), so u=1 IS the target
  const mid = morphAAt(prep, 0.5).outline;
  assert.ok(mid.every((q, i) => Math.abs(q[0] - (A[i][0] + B[i][0]) / 2) < 1e-9), "the vertex lerp, nothing else");
});

test("xfRingPath writes a closed POLYLINE - never a cubic, so a landed bar is a bar and not a rounded one", () => {
  assert.equal(xfRingPath([[0, 0], [10, 0], [10, 5], [0, 5]]), "M0.0 0.0 L10.0 0.0 L10.0 5.0 L0.0 5.0 Z");
  assert.equal(xfRingPath([]), "");
});

test("xfRemakeClock: one clock, four phases, exact at both ends", () => {
  const z = xfRemakeClock(0);
  assert.deepEqual([z.leave, z.travel, z.hand, z.draw], [0, 0, 0, 0], "u=0 is the exact source: nothing has begun");
  const o = xfRemakeClock(1);
  assert.deepEqual([o.leave, o.travel, o.hand, o.draw], [1, 1, 1, 1], "u=1 is the exact target: every phase is done");
  assert.deepEqual(xfRemakeClock(-1), xfRemakeClock(0));
  assert.deepEqual(xfRemakeClock(2), xfRemakeClock(1));
  const half = xfRemakeClock(0.5);
  assert.equal(half.leave, 1, "the source's ink has left by half the clock");
  assert.ok(half.travel > 0 && half.travel < 1, "and the rings are in flight");
  assert.equal(half.hand, 0, "nothing of the target's own ink has taken over yet");
});

test("REMAKE's phases are ordered and inside the clock", () => {
  assert.ok(0 < REMAKE.LEAVE && REMAKE.LEAVE < REMAKE.DRAW && REMAKE.DRAW < REMAKE.TRAVEL && REMAKE.TRAVEL < 1);
  assert.ok(REMAKE.COLS >= 4);
});

test("xfRemakeClock's travel ends where the TARGET's own ink begins: at TRAVEL for bars, at DRAW for a line", () => {
  assert.equal(xfRemakeClock(REMAKE.TRAVEL).travel, 1);
  assert.ok(xfRemakeClock(REMAKE.DRAW).travel < 1, "a bars target is still travelling at DRAW");
  assert.equal(xfRemakeClock(REMAKE.DRAW, true).travel, 1, "a LINE target's rings have landed before its line strokes");
  assert.equal(xfRemakeClock(1, true).travel, 1);
  assert.equal(xfRemakeClock(0, true).travel, 0);
});

test("xfRemakeTravel: the ink is in the columns before the columns have gone anywhere", () => {
  const a = xfRemakeTravel(0);
  assert.deepEqual([a.ink, a.move], [0, 0]);
  assert.equal(xfRemakeTravel(REMAKE_BEAT.INK).ink, 1);
  assert.equal(xfRemakeTravel(REMAKE_BEAT.MOVE).move, 0);
  assert.ok(xfRemakeTravel(REMAKE_BEAT.INK).move < 0.2, "by the time the ink has landed the shapes have barely moved");
  const z = xfRemakeTravel(1);
  assert.deepEqual([z.ink, z.move], [1, 1]);
});
