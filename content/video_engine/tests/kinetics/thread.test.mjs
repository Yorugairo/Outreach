/* HF-16 (P50 T15) - THE WIRE: one element carried across a page boundary.

   The claim the module makes is geometric and exact: the carried mark stands on the SAME STAGE PIXELS it stood on
   before the cut, whatever the two pages' own drawing units are. Everything here tests that claim, plus the pose
   (already drawn on the first frame - nothing arrives from anywhere) and the two refusals. */
import test from "node:test";
import assert from "node:assert/strict";
import { THREAD, threadFit, threadToStage, threadToLocal, threadCarry, threadWidth, threadPose, threadPath } from "../../scripts/species/thread.mjs";

/* two REAL pages, measured 2026-09-11 by scripts/measure_page_boxes.py at 9:16: a dense-line page whose chart box is
   800 x 680 with an 800 x 851 viewBox, and a bars page whose chart box is 800 x 882 with an 800 x 602 viewBox. */
const SRC_BOX = { x: 80, y: 526, w: 800, h: 680 }, SRC_VB = [800, 851];
const DST_BOX = { x: 80, y: 324, w: 800, h: 882 }, DST_VB = [800, 602];

test("a fit is the browser's own containment: uniform scale, centred in the box", () => {
  const f = threadFit(SRC_BOX, ...SRC_VB);
  assert.equal(f.s, Math.min(800 / 800, 680 / 851));
  /* centred: the same air above and below */
  assert.ok(Math.abs((f.ty - SRC_BOX.y) - ((SRC_BOX.y + SRC_BOX.h) - (f.ty + SRC_VB[1] * f.s))) < 1e-9);
  assert.ok(Math.abs((f.tx - SRC_BOX.x) - ((SRC_BOX.x + SRC_BOX.w) - (f.tx + SRC_VB[0] * f.s))) < 1e-9);
});

test("stage and local are each other's inverse to the bit", () => {
  const f = threadFit(DST_BOX, ...DST_VB);
  for (const p of [[0, 0], [123.5, 456.25], [800, 602]]) {
    const back = threadToLocal(f, threadToStage(f, p));
    assert.ok(Math.abs(back[0] - p[0]) < 1e-9 && Math.abs(back[1] - p[1]) < 1e-9, JSON.stringify([p, back]));
  }
});

test("THE CARRY: the wire stands on the same stage pixels after the cut", () => {
  const sf = threadFit(SRC_BOX, ...SRC_VB), df = threadFit(DST_BOX, ...DST_VB);
  const pts = [[150, 700], [300, 520], [480, 610], [730, 210]];
  const carried = threadCarry(pts, sf, df);
  assert.equal(carried.length, pts.length);
  for (let i = 0; i < pts.length; i++) {
    const was = threadToStage(sf, pts[i]), now = threadToStage(df, carried[i]);
    assert.ok(Math.abs(was[0] - now[0]) < 1e-9 && Math.abs(was[1] - now[1]) < 1e-9,
      `point ${i} moved: ${JSON.stringify(was)} -> ${JSON.stringify(now)}`);
  }
});

test("two pages with the SAME fit carry the wire unchanged - the identity costs nothing", () => {
  const f = threadFit(SRC_BOX, ...SRC_VB);
  const pts = [[10, 20], [30, 40]];
  const carried = threadCarry(pts, f, f);
  for (let i = 0; i < pts.length; i++)
    assert.ok(Math.abs(carried[i][0] - pts[i][0]) < 1e-9 && Math.abs(carried[i][1] - pts[i][1]) < 1e-9);
});

test("the stroke carries with the line: the same pixels wide, thinned to a ground line", () => {
  const sf = threadFit(SRC_BOX, ...SRC_VB), df = threadFit(DST_BOX, ...DST_VB);
  const w = threadWidth(6, sf, df);
  assert.ok(Math.abs(w - 6 * (sf.s / df.s) * THREAD.WIDTH) < 1e-9);
  assert.ok(w * df.s < 6 * sf.s, "a ground line is thinner on screen than the argument it was");
  assert.equal(threadWidth(0, sf, df) >= 1, true, "never a hairline that disappears");
});

test("fewer than two points is not a line, and nothing is carried", () => {
  const f = threadFit(SRC_BOX, ...SRC_VB);
  assert.equal(threadCarry([[1, 2]], f, f), null);
  assert.equal(threadCarry([], f, f), null);
  assert.equal(threadCarry(null, f, f), null);
  assert.equal(threadPath(null), "");
  assert.equal(threadPath([[1, 2]]), "");
});

test("THE POSE: already drawn at the page's first frame, receding to a ground line - a pure function of t", () => {
  assert.deepEqual(threadPose(0), { drawn: 1, alpha: THREAD.FROM });
  assert.ok(Math.abs(threadPose(THREAD.FADE_S).alpha - THREAD.ALPHA) < 1e-12);
  assert.equal(threadPose(99).alpha, threadPose(THREAD.FADE_S).alpha, "it holds after the recede - nothing keeps moving");
  assert.equal(threadPose(-5).alpha, THREAD.FROM, "before the page, the page's first frame");
  const a = threadPose(0.45).alpha;
  assert.ok(a < THREAD.FROM && a > THREAD.ALPHA, a);
  for (let i = 0; i <= 10; i++) assert.equal(threadPose(i / 10).alpha, threadPose(i / 10).alpha);
  assert.equal(threadPose(0).drawn, 1, "the wire never draws on: it was already there");
});

test("the path is the polyline it was, to two decimals", () => {
  assert.equal(threadPath([[1.005, 2], [3, 4.5]]), "M1.00 2.00 L3.00 4.50");
});
