// P61 T3 / R26-117 + P48 T5b / R26-16 - THE SOURCE A PAGE-ENTER MORPH STARTS FROM. Two pure pieces and the law that
// joins them: `arap.polyStrip` re-expresses ANY closed outline as the strip of columns `stripMesh` carries (the
// topology that never inverts on the area under a series), and `contour.contourSilhouette` produces such an outline
// from a still's own pixels - a planted element's silhouette, ours, no library. The melt's ball and a traced blob go
// through the same door, which is the whole point: the ring is geometry, and the page cannot tell them apart.
import { test } from "node:test";
import assert from "node:assert/strict";
import { STRIP, polyStrip, stripMesh, stripOutline, arapPrepareMesh, arapAt, minDet, bbox, polyArea }
  from "../../scripts/kinetics/arap.mjs";
import { contourSilhouette, contourLuma, contourBitmap } from "../../scripts/kinetics/contour.mjs";
import { MELT, MELT_ENDINGS, meltOpts, meltHandAt, meltHandDelay, meltHandSecs, meltHandRing }
  from "../../scripts/species/melt.mjs";

/* the two fixtures: a circle (the ball) and a lobed star-shaped blob (a planted element) */
const circle = (cx, cy, r, n = 96) =>
  [...Array(n).keys()].map((i) => { const t = (i / n) * Math.PI * 2; return [cx + r * Math.cos(t), cy + r * Math.sin(t)]; });
const lobed = (cx, cy, r, n = 120) =>
  [...Array(n).keys()].map((i) => { const t = (i / n) * Math.PI * 2, R = r * (1 + 0.22 * Math.cos(3 * t + 0.6) + 0.12 * Math.sin(5 * t - 0.3));
                                    return [cx + R * Math.cos(t), cy + R * Math.sin(t)]; });
/* the target every page-enter morph lands on: the area under a series, as a strip of the same columns */
const areaUnder = (n) => {
  const xs = [...Array(n).keys()].map((i) => 100 + (i / (n - 1)) * 800);
  return { top: xs.map((x, i) => [x, 400 - 120 * Math.sin(i / 6) - i]), bot: xs.map((x) => [x, 500]) };
};
const bmpOf = (w, h, ink) => { const data = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) data[y * w + x] = ink(x, y) ? 1 : 0; return { w, h, data }; };

/* ---- polyStrip ------------------------------------------------------------------------------------------------ */
test("the strip's two guards are frozen dials", () => {
  assert.equal(Object.isFrozen(STRIP), true);
  assert.ok(STRIP.EPS_X > 0 && STRIP.MIN_H > 0, "both guards are about the MESH, not the picture");
});

test("a circle becomes a strip of n columns that stands on the circle", () => {
  const S = polyStrip(circle(500, 300, 80), 48);
  assert.equal(S.n, 48);
  assert.equal(S.top.length, 48);
  assert.equal(S.bot.length, 48);
  for (let i = 0; i < 48; i++) {
    assert.equal(S.top[i][0], S.bot[i][0], "a column is one x");
    assert.ok(S.top[i][1] < S.bot[i][1], `column ${i} has a height`);
    const dx = S.top[i][0] - 500, half = Math.sqrt(Math.max(0, 80 * 80 - dx * dx));
    /* the sampled circle is a 96-gon, so the true half-height is a hair under the analytic one */
    assert.ok(Math.abs((S.bot[i][1] - S.top[i][1]) / 2 - half) < 1.5 + 80 * STRIP.MIN_H,
              `column ${i} sits on the circle`);
  }
});

test("no column is degenerate, even at the two ends where a vertical line is a tangent", () => {
  const S = polyStrip(circle(500, 300, 80), 48), B = bbox(circle(500, 300, 80));
  for (const i of [0, 47]) assert.ok(S.bot[i][1] - S.top[i][1] >= B.h * STRIP.MIN_H - 1e-9,
                                     "the end columns are opened to the minimum height");
});

test("a lobed silhouette keeps its lobes: the column heights are not monotone", () => {
  const S = polyStrip(lobed(500, 300, 80), 48);
  const h = S.top.map((p, i) => S.bot[i][1] - p[1]);
  let turns = 0;
  for (let i = 1; i + 1 < h.length; i++) if ((h[i] - h[i - 1]) * (h[i + 1] - h[i]) < 0) turns++;
  assert.ok(turns >= 2, `a lobed form's column heights turn (turns=${turns})`);
});

test("it refuses what is not an outline, and never guesses", () => {
  assert.equal(polyStrip([[0, 0], [1, 1]], 48), null, "two points are not an outline");
  assert.equal(polyStrip([], 48), null);
  assert.equal(polyStrip(null, 48), null);
  assert.equal(polyStrip([[0, 0], [1, 0], [2, 0]], 48), null, "a degenerate box has no strip");
});

test("it is a pure function: the same outline and n give the same strip, vertex for vertex", () => {
  const p = lobed(500, 300, 80);
  assert.deepEqual(polyStrip(p, 48), polyStrip(p, 48));
});

/* ---- the morph the strip is built for ---------------------------------------------------------------------------- */
test("a ball's ring morphs into the area under a line with det J > 0 at every frame", () => {
  const n = 48, S = polyStrip(circle(500, 300, 80), n), T = areaUnder(n);
  const mesh = stripMesh(S.top, S.bot);
  const prep = arapPrepareMesh(mesh, [...T.top, ...T.bot], n + (n >> 1));
  for (const t of [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1]) {
    const d = minDet(prep, t);
    assert.ok(d.target > 0, `t=${t}: the interpolated Jacobians never invert (${d.target})`);
    assert.ok(d.solved > 0, `t=${t}: nor does the solved mesh (${d.solved})`);
  }
});

test("u = 0 is the source exactly and u = 1 is the target exactly, and two calls agree", () => {
  const n = 48, S = polyStrip(lobed(500, 300, 80), n), T = areaUnder(n);
  const mesh = stripMesh(S.top, S.bot);
  const prep = arapPrepareMesh(mesh, [...T.top, ...T.bot], n + (n >> 1));
  const A = stripOutline(mesh.verts, n), B = stripOutline([...T.top, ...T.bot], n);
  const at0 = arapAt(prep, 0).outline, at1 = arapAt(prep, 1).outline;
  for (let i = 0; i < A.length; i++) {
    assert.ok(Math.hypot(at0[i][0] - A[i][0], at0[i][1] - A[i][1]) < 1e-6, `vertex ${i} at u=0 is the source`);
    assert.ok(Math.hypot(at1[i][0] - B[i][0], at1[i][1] - B[i][1]) < 1e-6, `vertex ${i} at u=1 is the target`);
  }
  assert.deepEqual(arapAt(prep, 0.37).outline, arapAt(prep, 0.37).outline);
});

test("at u = 0.5 the shape is NEITHER the ball nor the area - the frame a cut cannot make", () => {
  const n = 48, S = polyStrip(circle(500, 300, 80), n), T = areaUnder(n);
  const mesh = stripMesh(S.top, S.bot);
  const prep = arapPrepareMesh(mesh, [...T.top, ...T.bot], n + (n >> 1));
  const A = stripOutline(mesh.verts, n), B = stripOutline([...T.top, ...T.bot], n);
  const mid = arapAt(prep, 0.5).outline;
  const far = (P, Q) => Math.max(...P.map((p, i) => Math.hypot(p[0] - Q[i][0], p[1] - Q[i][1])));
  assert.ok(far(mid, A) > 20, "not the ball");
  assert.ok(far(mid, B) > 20, "not the area");
  assert.ok(Math.abs(polyArea(mid)) > 0, "and it is still a shape with an inside");
});

/* ---- the tracer ------------------------------------------------------------------------------------------------ */
test("contourSilhouette returns ONE closed ring - the largest, holes discarded", () => {
  /* an "O": an outer ring and its hole. A silhouette is the outer one; the hole is not a silhouette. */
  const O = bmpOf(9, 9, (x, y) => (x >= 1 && x <= 7 && y >= 1 && y <= 7) && !(x >= 3 && x <= 5 && y >= 3 && y <= 5));
  const pts = contourSilhouette(O);
  assert.ok(Array.isArray(pts) && pts.length >= 3);
  const B = bbox(pts);
  assert.ok(B.w >= 6 && B.h >= 6, "it is the OUTER ring, not the 3x3 hole");
});

test("it traces a lobed form off its own raster, and the trace stands on the form", () => {
  const W = 120, H = 90, cx = 58, cy = 44, r = 26;
  const rAt = (th) => r * (1 + 0.22 * Math.cos(3 * th + 0.6) + 0.12 * Math.sin(5 * th - 0.3));
  const ink = (x, y) => Math.hypot(x - cx, y - cy) <= rAt(Math.atan2(y - cy, x - cx));
  const pts = contourSilhouette(bmpOf(W, H, ink), { tol: 0.6 });
  assert.ok(pts.length >= 3 && pts.length < 200, `simplified, not raw (${pts.length})`);
  for (const p of pts) {
    const d = Math.hypot(p[0] - cx, p[1] - cy), R = rAt(Math.atan2(p[1] - cy, p[0] - cx));
    assert.ok(Math.abs(d - R) < 2.0, `a traced vertex sits on the form (|${d.toFixed(2)} - ${R.toFixed(2)}|)`);
  }
});

test("a traced silhouette goes straight into polyStrip, which is the door the ball uses", () => {
  const W = 120, H = 90, cx = 58, cy = 44, r = 26;
  const rAt = (th) => r * (1 + 0.22 * Math.cos(3 * th + 0.6) + 0.12 * Math.sin(5 * th - 0.3));
  const pts = contourSilhouette(bmpOf(W, H, (x, y) => Math.hypot(x - cx, y - cy) <= rAt(Math.atan2(y - cy, x - cx))), { tol: 0.6 });
  const n = 48, S = polyStrip(pts, n), T = areaUnder(n);
  assert.ok(S, "a traced ring is a strip");
  const prep = arapPrepareMesh(stripMesh(S.top, S.bot), [...T.top, ...T.bot], n + (n >> 1));
  for (const t of [0, 0.5, 1]) assert.ok(minDet(prep, t).target > 0, `t=${t}: no inversion on a traced source`);
});

test("it is null when the raster holds no ink - a caller never gets a poly it did not measure", () => {
  assert.equal(contourSilhouette(bmpOf(8, 8, () => false)), null);
});

test("contourLuma reads dark ink on a light ground, and its mirror", () => {
  const W = 6, H = 4, px = new Uint8Array(W * H * 4);
  for (let i = 0; i < W * H; i++) { const dark = (i % W) >= 2 && (i % W) <= 3;
    px[i * 4] = px[i * 4 + 1] = px[i * 4 + 2] = dark ? 20 : 240; px[i * 4 + 3] = 255; }
  const dk = contourLuma(px, W, H, 0.5);
  const lt = contourLuma(px, W, H, 0.5, { dark: false });
  for (let i = 0; i < W * H; i++) assert.equal(dk.data[i] + lt.data[i], 1, "every sample is ink on exactly one side");
  assert.equal(dk.data[2], 1, "the dark columns are ink");
  assert.equal(dk.data[0], 0, "the cream ground is not");
});

test("an alpha bitmap and a luma bitmap of the same shape trace to the same silhouette", () => {
  const W = 40, H = 30, ink = (x, y) => Math.hypot(x - 20, y - 15) <= 9;
  const alpha = new Uint8Array(W * H * 4), luma = new Uint8Array(W * H * 4);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const i = (y * W + x) * 4, on = ink(x, y);
    alpha[i + 3] = on ? 255 : 0;
    luma[i] = luma[i + 1] = luma[i + 2] = on ? 10 : 250; luma[i + 3] = 255; }
  assert.deepEqual(contourSilhouette(contourBitmap(alpha, W, H)), contourSilhouette(contourLuma(luma, W, H, 0.5)));
});

/* ---- the melt's side of the hand-over ---------------------------------------------------------------------------- */
test("`morph` is the fourth authored ending, and the grammar refuses a word it does not have", () => {
  assert.deepEqual([...MELT_ENDINGS], ["throw", "splash:chart", "splash:plate", "morph"]);
  assert.equal(meltOpts("melt:morph").ending, "morph");
  assert.equal(meltOpts("melt").ending, "throw", "the default is untouched");
  assert.throws(() => meltOpts("melt:morphh"), /morphh/);
  assert.throws(() => meltOpts("melt:morph:throw"), /two endings/);
  assert.throws(() => meltOpts("melt:weight:morph:metal"), /two endings|metal/);
});

test("a bare melt's window is untouched; a morph's window makes room for the hand", () => {
  assert.equal(meltOpts("melt").secs, MELT.S);
  assert.equal(meltOpts("melt:morph").secs, MELT.S + MELT.M_S);
  assert.equal(meltOpts("melt:morph:3").secs, 3, "a row that declares its own length gets exactly it");
});

test("the hand-over splits the window once: the melt's end IS the page's morph's end", () => {
  const o = meltOpts("melt:morph"), at = meltHandAt(o);
  assert.ok(at > 0 && at < 1);
  assert.equal(meltHandDelay(o, true) + meltHandSecs(o), o.secs, "one clock, no gap");
  assert.equal(meltHandDelay(o, false), 0, "a world that is not a page is handed nothing");
  assert.equal(meltHandDelay(meltOpts("melt"), true), 0, "and neither is a throw");
  assert.equal(meltHandDelay(meltOpts("melt:splash:chart"), true), 0);
});

test("the ring handed over is the ball's own circle, and it is a pure function of the box and the seed", () => {
  const rect = { x: 100, y: 80, w: 900, h: 480 }, rnd = (k) => ((k * 2654435761) % 1000) / 1000;
  const o = Object.assign({ rect }, meltOpts("melt:morph"));
  const h = meltHandRing(o, rnd);
  assert.equal(h.ring.length, MELT.CIRCLE_N);
  for (const p of h.ring) assert.ok(Math.abs(Math.hypot(p[0] - h.c[0], p[1] - h.c[1]) - h.r) < 1e-6, "a circle, exactly");
  assert.deepEqual(meltHandRing(o, rnd), h, "twice is the same ring");
  assert.equal(meltHandRing(Object.assign({}, o, { rect: null }), rnd), null, "no ink box, no ring");
});

test("the handed ring goes through polyStrip and morphs without inverting - the two halves are one door", () => {
  const rect = { x: 100, y: 80, w: 900, h: 480 }, rnd = (k) => ((k * 2654435761) % 1000) / 1000;
  const h = meltHandRing(Object.assign({ rect }, meltOpts("melt:morph")), rnd);
  const n = 48, S = polyStrip(h.ring, n), T = areaUnder(n);
  const prep = arapPrepareMesh(stripMesh(S.top, S.bot), [...T.top, ...T.bot], n + (n >> 1));
  for (const t of [0, 0.5, 1]) assert.ok(minDet(prep, t).target > 0, `t=${t}`);
});
