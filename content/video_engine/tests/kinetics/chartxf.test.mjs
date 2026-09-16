// P48 T2 - the chart-transition interpolators: exact at both ends, linear between, fades that respect the domain.
import { test } from "node:test";
import assert from "node:assert/strict";
import { xfLerp, xfPoint, xfPath, xfFade, xfInside, xfRect, XF,
         xfSpanTop, xfStripRing, xfBarRing, xfRingPath, xfRemakeClock, xfRemakeTravel, REMAKE, REMAKE_BEAT,
         xfRemakeLineClock, xfGatherK, xfRingTo, xfDrawWindow, REMAKE_LINE } from "../../scripts/kinetics/chartxf.mjs";
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

test("xfRemakeClock: one clock, three phases, exact at both ends", () => {
  const z = xfRemakeClock(0);
  assert.deepEqual([z.leave, z.travel, z.hand], [0, 0, 0], "u=0 is the exact source: nothing has begun");
  const o = xfRemakeClock(1);
  assert.deepEqual([o.leave, o.travel, o.hand], [1, 1, 1], "u=1 is the exact target: every phase is done");
  assert.deepEqual(xfRemakeClock(-1), xfRemakeClock(0));
  assert.deepEqual(xfRemakeClock(2), xfRemakeClock(1));
  const half = xfRemakeClock(0.5);
  assert.equal(half.leave, 1, "the source's ink has left by half the clock");
  assert.ok(half.travel > 0 && half.travel < 1, "and the rings are in flight");
  assert.equal(half.hand, 0, "nothing of the target's own ink has taken over yet");
});

test("REMAKE's phases are ordered and inside the clock", () => {
  assert.ok(0 < REMAKE.LEAVE && REMAKE.LEAVE < REMAKE.TRAVEL && REMAKE.TRAVEL < 1);
  assert.ok(REMAKE.COLS >= 4);
});

test("xfRemakeClock's travel ends where the TARGET's own bars begin, at REMAKE.TRAVEL", () => {
  assert.equal(xfRemakeClock(REMAKE.TRAVEL).travel, 1);
  assert.equal(xfRemakeClock(REMAKE.TRAVEL).hand, 0, "the hand-over starts exactly where the travel ends");
  assert.ok(xfRemakeClock(REMAKE.LEAVE + 0.01).travel > 0 && xfRemakeClock(REMAKE.LEAVE).travel === 0);
});

// ---- P61 T2b (E99 s39) - BARS -> LINE: the collapse to the apex, and the draw back to the root -----
test("xfRemakeLineClock: gather, settle, draw, hand - exact at both ends, pure in u", () => {
  const z = xfRemakeLineClock(0);
  assert.deepEqual([z.gather, z.settle, z.draw, z.hand], [0, 0, 0, 0], "u=0 is the exact bars page");
  const o = xfRemakeLineClock(1);
  assert.deepEqual([o.gather, o.settle, o.draw, o.hand], [1, 1, 1, 1], "u=1 is the whole line, drawn");
  assert.deepEqual(xfRemakeLineClock(-1), xfRemakeLineClock(0));
  assert.deepEqual(xfRemakeLineClock(2), xfRemakeLineClock(1));
  assert.equal(xfRemakeLineClock(REMAKE_LINE.GATHER).gather, 1, "every bar's ink is at the apex by GATHER");
  assert.equal(xfRemakeLineClock(REMAKE_LINE.GATHER).settle, 0, "and only then does the point carry itself");
  assert.equal(xfRemakeLineClock(REMAKE_LINE.SETTLE).settle, 1);
  assert.equal(xfRemakeLineClock(REMAKE_LINE.SETTLE).draw, 0, "the stroke starts where the point lands - never before");
});

test("at half the clock the frame is the POINT and a PARTIAL stroke - the ruling's own instant", () => {
  const h = xfRemakeLineClock(0.5);
  assert.equal(h.gather, 1, "the bars' ink is gathered");
  assert.equal(h.settle, 1, "the point stands on the line's own apex datum");
  assert.ok(h.draw > 0.05 && h.draw < 0.95, `the line is part drawn, not formed: ${h.draw}`);
  assert.equal(h.hand, 0, "and nothing has handed over");
  assert.ok(REMAKE_LINE.GATHER < REMAKE_LINE.SETTLE && REMAKE_LINE.SETTLE < 0.5 && REMAKE_LINE.HOLD < 1);
});

test("xfGatherK: the FARTHEST ring leaves first and every ring lands together", () => {
  assert.equal(xfGatherK(1, 0, 5, 0.25), 1);
  assert.equal(xfGatherK(1, 4, 5, 0.25), 1, "they land together - a collapse ends as ONE point");
  assert.equal(xfGatherK(0, 0, 5, 0.25), 0);
  assert.ok(xfGatherK(0.2, 0, 5, 0.25) > xfGatherK(0.2, 4, 5, 0.25), "rank 0 is the farthest, and it is already moving");
  assert.equal(xfGatherK(0.2, 4, 5, 0.25), 0, "the nearest has not started at a fifth of the gather");
  assert.equal(xfGatherK(0.5, 2, 1, 0.25), 0.5, "one ring has no stagger to spread");
  assert.equal(xfGatherK(0.5, 0, 5, 0), 0.5, "spread 0 is every ring on one clock");
});

test("xfRingTo takes every vertex to ONE point: at k=1 the ring has no area to carry ink", () => {
  const ring = xfBarRing({ x: 0, y: 100, w: 40, h: 100, base: 200 }, 4);
  assert.deepEqual(xfRingTo(ring, [10, 10], 0), ring, "k=0 is the bar, exactly");
  const gone = xfRingTo(ring, [10, 10], 1);
  assert.ok(gone.every((q) => q[0] === 10 && q[1] === 10), "k=1 is the point itself");
  const half = xfRingTo(ring, [0, 0], 0.5);
  assert.ok(half.every((q, i) => Math.abs(q[0] - ring[i][0] / 2) < 1e-9 && Math.abs(q[1] - ring[i][1] / 2) < 1e-9));
  assert.deepEqual(xfRingTo(null, [0, 0], 0.5), []);
});

test("xfDrawWindow grows out of the apex: the root side first, exact at both ends", () => {
  const z = xfDrawWindow(1, 0);
  assert.deepEqual([z.s, z.e], [1, 1], "k=0 is the bare point at the apex - no stroke at all");
  const o = xfDrawWindow(1, 1);
  assert.deepEqual([o.s, o.e], [0, 1], "k=1 is the whole path, root to apex");
  const h = xfDrawWindow(1, 0.5);
  assert.deepEqual([h.s, h.e], [0.5, 1], "half the path, drawn BACK from the apex");
  const mid = xfDrawWindow(0.4, 0.5);   // an apex in the middle: the far side draws with the root side, so u=1 is the whole line
  assert.deepEqual([mid.s, mid.e], [0.2, 0.7]);
  assert.deepEqual([xfDrawWindow(0.4, 1).s, xfDrawWindow(0.4, 1).e], [0, 1]);
  assert.deepEqual([xfDrawWindow(2, -1).s, xfDrawWindow(2, -1).e], [1, 1], "both arguments clamp");
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
