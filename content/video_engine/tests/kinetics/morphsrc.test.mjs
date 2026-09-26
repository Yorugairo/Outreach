// P61 T3 / R26-117 + P48 T5b / R26-16 - THE SOURCE A PAGE-ENTER MORPH STARTS FROM. Two pure pieces and the law that
// joins them: `arap.polyStrip` re-expresses ANY closed outline as the strip of columns `stripMesh` carries (the
// topology that never inverts on the area under a series), and `contour.contourSilhouette` produces such an outline
// from a still's own pixels - a planted element's silhouette, ours, no library. The melt's ball and a traced blob go
// through the same door, which is the whole point: the ring is geometry, and the page cannot tell them apart.
import { test } from "node:test";
import assert from "node:assert/strict";
import { STRIP, polyStrip, stripFor, stripMesh, stripOutline, arapPrepareMesh, arapAt, minDet, bbox, polyArea }
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

/* ---- P72 T24 / R26-150 + R26-163: the strip takes an axis, names the bay it fills, and `stripFor` picks the axis ---- */
const horseshoe = [[400, 200], [500, 200], [500, 235], [430, 235], [430, 285], [500, 285], [500, 320], [400, 320]];   /* opens right */
const inPoly = (pt, poly) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const a = poly[i], b = poly[j];
  if ((a[1] > pt[1]) !== (b[1] > pt[1]) && pt[0] < (b[0] - a[0]) * (pt[1] - a[1]) / (b[1] - a[1]) + a[0]) c = !c; } return c; };

test("axis 0 is the x strip to the digit, and the ball and the lobed blob fill no bay", () => {
  for (const p of [circle(500, 300, 80), lobed(500, 300, 80)]) {
    const S = polyStrip(p, 48), T = polyStrip(p, 48, { axis: 0 });
    assert.deepEqual([S.top, S.bot], [T.top, T.bot]);
    assert.equal(S.axis, 0);
    assert.deepEqual(S.bays, [], "a fold under BAY_MIN of the area is not a bay");
  }
});

test("the x strip names the horseshoe's bay; stripFor turns the strip across the opening and keeps it", () => {
  const S = polyStrip(horseshoe, 48);
  assert.equal(S.bays.length, 1);
  assert.ok(S.bays[0].share > STRIP.BAY_MIN, "the bay is a share of the shape's area");
  const n = 48, T = areaUnder(n), R = stripFor(horseshoe, [...T.top, ...T.bot], n, n + (n >> 1));
  const out = stripOutline([...R.top, ...R.bot], n);
  assert.equal(R.refused, null);
  assert.deepEqual(R.bays, []);
  assert.ok(R.det > 0, "and it never inverts");
  assert.equal(inPoly([465, 260], out), false, "the bay stays open");
  assert.ok(inPoly([465, 215], out) && inPoly([465, 305], out) && inPoly([415, 260], out), "the arms and the back are carried");
});

test("stripFor is pure and keeps a sound x strip", () => {
  const n = 48, T = areaUnder(n), B = [...T.top, ...T.bot], p = lobed(500, 300, 80);
  const a = stripFor(p, B, n, n + (n >> 1)), b = stripFor(p, B, n, n + (n >> 1)), x = polyStrip(p, n);
  assert.deepEqual(a, b);
  assert.equal(a.axis, 0);
  assert.deepEqual([a.top, a.bot], [x.top, x.bot]);
  assert.equal(stripFor(null, B, n), null);
});

/* THE TIE (P61 T3d's real beat), as the player hands it to stripFor: the traced silhouette in the page's own chart px and
   the area under its series, rounded to 0.1 px (measured off build-p61-planted by the P72 T24 probe) */
const TIE = [[294.7,428.2],[296.2,427.7],[297.2,428.7],[299.2,428.7],[301.6,431.1],[301.6,434.1],[303.6,439.0],[303.6,444.0],[304.6,445.0],[304.6,449.9],[306.6,454.9],[306.6,460.8],[309.6,468.7],[309.6,471.7],[310.6,472.7],[310.6,475.7],[312.5,480.6],[312.5,484.6],[313.5,485.6],[313.5,488.5],[315.5,493.5],[315.5,500.4],[312.5,505.3],[312.5,507.3],[304.1,517.7],[299.2,517.7],[285.8,503.4],[282.8,499.4],[282.8,497.4],[281.8,496.4],[282.8,466.8],[283.8,465.8],[283.8,461.8],[282.8,459.8],[283.8,458.8],[283.8,448.9],[284.8,447.9],[284.8,446.0],[283.8,445.0],[284.8,444.0],[284.8,434.1],[288.3,429.6]];
const TIE_TARGET = [[150,715.1],[162.3,720.0],[174.7,726.7],[187.0,721.1],[199.4,711.3],[211.7,682.3],[224.0,633.3],[236.4,547.4],[248.7,495.3],[261.1,504.4],[273.4,513.9],[285.7,531.9],[298.1,542.6],[310.4,545.5],[322.8,562.7],[335.1,533.8],[347.4,513.8],[359.8,467.4],[372.1,441.8],[384.5,392.1],[396.8,369.8],[409.1,282.7],[421.5,251.3],[433.8,256.8],[446.2,231.5],[458.5,197.5],[470.9,187.5],[483.2,190.8],[495.5,232.0],[507.9,236.8],[520.2,264.2],[532.6,254.6],[544.9,280.9],[557.2,300.7],[569.6,272.9],[581.9,224.5],[594.3,162.2],[606.6,164.4],[618.9,156.0],[631.3,141.2],[643.6,184.1],[656.0,267.9],[668.3,258.5],[680.6,224.4],[693.0,258.8],[705.3,238.8],[717.7,201.8],[730,249.4],[150,771],[162.3,771],[174.7,771],[187.0,771],[199.4,771],[211.7,771],[224.0,771],[236.4,771],[248.7,771],[261.1,771],[273.4,771],[285.7,771],[298.1,771],[310.4,771],[322.8,771],[335.1,771],[347.4,771],[359.8,771],[372.1,771],[384.5,771],[396.8,771],[409.1,771],[421.5,771],[433.8,771],[446.2,771],[458.5,771],[470.9,771],[483.2,771],[495.5,771],[507.9,771],[520.2,771],[532.6,771],[544.9,771],[557.2,771],[569.6,771],[581.9,771],[594.3,771],[606.6,771],[618.9,771],[631.3,771],[643.6,771],[656.0,771],[668.3,771],[680.6,771],[693.0,771],[705.3,771],[717.7,771],[730,771]];

test("the tie's x strip folds and is KEPT, the fold named - never turned away (the parent's ruling)", () => {
  const n = 48, R = stripFor(TIE, TIE_TARGET, n, n + (n >> 1)), x = polyStrip(TIE, n);
  assert.equal(R.axis, 0, "the approved upright strip");
  assert.deepEqual([R.top, R.bot], [x.top, x.bot], "vertex for vertex");
  assert.equal(R.refused, "fold");
  assert.ok(R.det <= 0 && R.fold.min_det <= 0);
  assert.equal(R.fold.column, R.fold.triangle >> 1);
  assert.ok(0 < R.fold.t0 && R.fold.t0 <= R.fold.worst_t && R.fold.worst_t <= R.fold.t1 && R.fold.t1 < 1, JSON.stringify(R.fold));
  assert.deepEqual(R.tried.map((r) => r.axis_deg), [0], "no other axis is read when the x strip keeps the shape");
});
