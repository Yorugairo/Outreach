// P69 T36 - THE LIT STRETCH (E99 s99: "a highlight that TRAVELS along a length ... counts as motion"; the Bravos
// harvest v2 A11 + A13, rank 1). A light runs along a stretch of ONE drawn series, from `from` to `to`, on its word,
// and the rest of the line keeps its ink. These tests pin the stretch on the live points (the span's own edge law),
// the travel clock, the clip to the ink that is actually drawn, the leave, and the painter reached only through ctx.
import { test } from "node:test";
import assert from "node:assert/strict";
import { LIT, litStretchPts, litLength, litCut, litClipX, litPose, litLeave, litPathD, litDrawnX,
         paintLitStretch } from "../../scripts/species/lit_stretch.mjs";

const near = (a, b, eps = 1e-6) => Math.abs(a - b) <= eps;
/* lpPointsNow's own shape: the PAGE's datum index and the point in the chart's viewBox */
const line = (n, off = 0, x0 = 100, x1 = 900, y = (j) => 300 - j) =>
  Array.from({ length: n }, (_, j) => ({ i: off + j, p: [x0 + (x1 - x0) * j / (n - 1), y(j)] }));
const sp = (o = {}) => Object.assign({ kind: "lit_stretch", at: 10, dur: 2, from: 20, to: 60 }, o);

test("the dials are the light's: it travels over most of its word and is drawn wider than the line it lights", () => {
  assert.ok(LIT.TRAVEL > 0.5 && LIT.TRAVEL <= 1, "the head takes most of the word, and lands inside it");
  assert.ok(LIT.CORE_K > 1, "the lit core is wider than the series' own stroke, or it hides under it");
  assert.ok(LIT.GLOW_K > LIT.CORE_K && LIT.GLOW_A > 0 && LIT.GLOW_A <= 1);
  assert.ok(LIT.HEAD_K > LIT.CORE_K / 2 && LIT.HEAD_OUT_S > 0 && LIT.MIN_LEN > 0);
});

// ---------------------------------------------------------------- the stretch
test("an index stretch is the series' own points from `from` to `to`, in TRAVEL order", () => {
  const pts = line(101);
  const s = litStretchPts(pts, 20, 60);
  assert.equal(s.length, 41);
  assert.deepEqual(s[0], pts[20].p);
  assert.deepEqual(s[40], pts[60].p);
  const back = litStretchPts(pts, 60, 20);
  assert.deepEqual(back[0], pts[60].p, "from > to: the light runs the other way, from `from`");
  assert.deepEqual(back[40], pts[20].p);
});

test("a fraction stretch cuts the line at its x and reads its y there (the span's edge law)", () => {
  const pts = line(5, 0, 100, 900, (j) => 100 * j);   /* x 100, 300, 500, 700, 900; y 0 .. 400 */
  const s = litStretchPts(pts, 0.125, 0.625);          /* x 200 .. 600 */
  assert.ok(near(s[0][0], 200) && near(s[0][1], 50));
  assert.ok(near(s[s.length - 1][0], 600) && near(s[s.length - 1][1], 250));
  assert.deepEqual(s.slice(1, -1), [[300, 100], [500, 200]]);
});

test("an edge the window has DROPPED lights nothing - never the wrong stretch (R26-28)", () => {
  const pts = line(51, 30);   /* the window holds 30..80 */
  assert.equal(litStretchPts(pts, 10, 60), null);
  assert.equal(litStretchPts(pts, 40, 90), null);
  assert.notEqual(litStretchPts(pts, 40, 60), null);
  assert.equal(litStretchPts([], 0, 1), null);
  assert.equal(litStretchPts(pts, 40, 40), null, "a point is not a stretch");
});

// ---------------------------------------------------------------- the travel
test("the head travels by ARC LENGTH on the min-jerk clock and lands at TRAVEL of the word", () => {
  const p0 = litPose(sp(), 9.99), p1 = litPose(sp(), 10), pm = litPose(sp(), 10 + 2 * LIT.TRAVEL), pz = litPose(sp(), 11.9);
  assert.equal(p0.on, false);
  assert.equal(p1.on, true);
  assert.equal(p1.u, 0);
  assert.ok(near(litPose(sp(), 10 + 0.5 * 2 * LIT.TRAVEL).u, 0.5, 1e-9), "min-jerk is symmetric: half the time is half the stretch");
  assert.equal(pm.u, 1);
  assert.equal(pz.u, 1, "and it HOLDS lit - the light that has arrived is an annotation now (s91), the travel was the motion (s99)");
  assert.ok(litPose(sp(), 10.3).u < 0.3 * 1.0 / (2 * LIT.TRAVEL), "it leaves gently, never at speed");
});

test("the comet head is up while the light travels and fades after it lands", () => {
  const land = 10 + 2 * LIT.TRAVEL;
  assert.equal(litPose(sp(), 10.5).head, 1);
  assert.equal(litPose(sp(), land).head, 1);
  assert.ok(litPose(sp(), land + LIT.HEAD_OUT_S / 2).head < 1);
  assert.equal(litPose(sp(), land + LIT.HEAD_OUT_S + 0.01).head, 0);
});

test("the cut is the stretch's first s units of length, its end the head", () => {
  const pts = [[0, 0], [30, 40], [60, 80]];   /* two 50-long segments */
  assert.equal(litLength(pts), 100);
  const c = litCut(pts, 75);
  assert.deepEqual(c[0], [0, 0]);
  assert.equal(c.length, 3);
  assert.ok(near(c[2][0], 45) && near(c[2][1], 60));
  assert.deepEqual(litCut(pts, 500), pts, "past the end is the whole stretch");
  assert.deepEqual(litCut(pts, 0), [[0, 0]]);
});

test("the light never runs ahead of the INK: the stretch is clipped to the drawn x", () => {
  const pts = [[100, 0], [200, 100], [300, 0]];
  const c = litClipX(pts, 250);
  assert.equal(c.length, 3);
  assert.ok(near(c[2][0], 250) && near(c[2][1], 50));
  assert.deepEqual(litClipX(pts, null), pts, "no measure of the ink - nothing to clip");
  assert.deepEqual(litClipX(pts, 1000), pts);
  assert.equal(litClipX(pts, 50).length, 0, "an undrawn stretch has nothing to light");
});

test("the drawn x is read off the series' OWN strokes, the widest of them, never another series'", () => {
  const stroke = (si, len, off, xAt) => ({ si, len, p: { getAttribute: (k) => (k === "stroke-dashoffset" ? String(off) : null),
    style: { opacity: "" }, getPointAtLength: (L) => ({ x: xAt(L), y: 0 }) } });
  const paths = [stroke(0, 100, 50, (L) => 100 + L * 8), stroke(0, 100, 90, (L) => 100 + L), stroke(1, 100, 0, () => 999)];
  assert.equal(litDrawnX(paths, 0), 500, "half of series 0 drawn: x 100 + 50 * 8");
  assert.equal(litDrawnX(paths, 1), 999);
  assert.equal(litDrawnX(paths, 2), null, "a series with no stroke measures nothing");
  paths[0].p.style.opacity = "0";
  assert.equal(litDrawnX(paths, 0), 110, "an un-drawn (hidden) stroke is no ink");
});

test("it LEAVES with the line: an undraw or a replacing chart_to takes it on the verb's own clock", () => {
  assert.equal(litLeave(null, 50), 0, "nothing replaces the page: it stands");
  const lv = { at: 20, dur: 1 };
  assert.equal(litLeave(lv, 19.9), 0);
  assert.equal(litLeave(lv, 20.5), 0.5);
  assert.equal(litLeave(lv, 21), 1);
  assert.equal(litLeave(lv, 90), 1, "and it does not come back");
});

test("the path is one M and its Ls, one decimal", () => {
  assert.equal(litPathD([[1, 2], [3.14159, 4]]), "M1.0 2.0 L3.1 4.0");
  assert.equal(litPathD([]), "");
});

test("a seek IS the play: the same t gives the same pose in any order", () => {
  const ts = [10.2, 11.7, 10.9, 10.2, 12.4, 11.7];
  const a = ts.map((t) => JSON.stringify(litPose(sp(), t)));
  const b = [...ts].reverse().map((t) => JSON.stringify(litPose(sp(), t))).reverse();
  assert.deepEqual(a, b);
});

// ---------------------------------------------------------------- the painter
const rec = () => { const a = {}; return { a, setAttribute: (k, v) => { a[k] = String(v); }, getAttribute: (k) => a[k] ?? null, style: {} }; };
const built = (o = {}) => ({ sp: sp(o), si: 0, g: rec(), core: rec(), head: o.comet ? rec() : null, leave: o.leave || null });
const ctx = (pts) => ({ pointsNow: () => pts });

test("THE PAINTER draws nothing before its word, then a lit path that grows from `from` toward `to`", () => {
  const pts = line(101), st = { paths: [] };
  const b = built({ comet: true });
  paintLitStretch(b, 9.5, st, ctx(pts));
  assert.equal(b.g.a.opacity, "0");
  paintLitStretch(b, 10 + LIT.TRAVEL, st, ctx(pts));   /* u 0.5: half the stretch by length */
  assert.equal(b.g.a.opacity, "1.000");
  const d = b.core.a.d;
  assert.ok(d.startsWith("M" + pts[20].p[0].toFixed(1)), d);
  const lastX = +d.split(" L").pop().split(" ")[0];
  assert.ok(lastX > pts[20].p[0] + 100 && lastX < pts[60].p[0] - 100, "the head is mid-stretch: " + lastX);
  assert.equal(b.head.a.opacity, "1.000");
  assert.equal(b.head.a.cx, lastX.toFixed(1));
  paintLitStretch(b, 20, st, ctx(pts));
  assert.ok(b.core.a.d.endsWith(pts[60].p[0].toFixed(1) + " " + pts[60].p[1].toFixed(1)), "landed: the whole stretch, held");
  assert.equal(b.head.a.opacity, "0.000", "the head has gone; the stretch stays lit");
});

test("THE PAINTER hides the light when an edge leaves the window, and fades it on the page's leave", () => {
  const b = built({ leave: { at: 15, dur: 1 } });
  paintLitStretch(b, 12, { paths: [] }, ctx(line(20, 30)));
  assert.equal(b.g.a.opacity, "0", "edge 20 is not in the window 30..49");
  paintLitStretch(b, 15.5, { paths: [] }, ctx(line(101)));
  assert.equal(b.g.a.opacity, "0.500");
  paintLitStretch(b, 16, { paths: [] }, ctx(line(101)));
  assert.equal(b.g.a.opacity, "0");
});

test("the painter reaches the engine ONLY through ctx and its state - no clock, no random, no DOM of its own", async () => {
  const { readFile } = await import("node:fs/promises");
  const src = await readFile(new URL("../../scripts/species/lit_stretch.mjs", import.meta.url), "utf-8");
  for (const bad of ["Date.now", "performance.now", "Math.random", "document.", "window.", "requestAnimationFrame"]) {
    assert.ok(!src.includes(bad), bad);
  }
  assert.match(src.split(/\r?\n/)[0], /^\/\* SPACE: page \*\/$/);   // a Windows checkout is CRLF
  assert.match(src.trimEnd().split(/\r?\n/).pop(), /PAGE_PAINTERS\.lit_stretch = paintLitStretch;$/);
});
