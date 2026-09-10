// P48 T2 - the chart-transition interpolators: exact at both ends, linear between, fades that respect the domain.
import { test } from "node:test";
import assert from "node:assert/strict";
import { xfLerp, xfPoint, xfPath, xfFade, xfInside, xfRect, XF } from "../../scripts/kinetics/chartxf.mjs";

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
