// P71 T32 (was P69 T80) - THE LENS (the Bravos harvest v2's A57). A glass rises onto a line on its word, travels the
// stretch from -> to (or stands on `from`), and leaves; inside its ring it redraws the page's OWN data at `zoom` about its
// centre. These tests pin the clock, the stand, the magnification (every vertex a datum, nothing past the pen), the parts
// and the painter reached only through ctx.
import { test } from "node:test";
import assert from "node:assert/strict";
import { LENS, lensZoom, lensPose, lensStand, lensMagnify, lensParts, paintLens } from "../../scripts/species/lens.mjs";

const near = (a, b, eps = 1e-6) => Math.abs(a - b) <= eps;
const sp = (o = {}) => Object.assign({ kind: "lens", at: 10, dur: 2.5, from: 3, to: 6 }, o);
const line = (n = 10) => Array.from({ length: n }, (_, i) => ({ i, p: [100 + 50 * i, 400 - 10 * i + (i === 5 ? 25 : 0)] }));

test("the dials are the reference's: the ring, the handle, the clock; the default glass magnifies nothing (E38)", () => {
  assert.equal(LENS.ZOOM, 1, "Bravos's glass, measured: k = 1.0 (STK 557.5)");
  assert.ok(LENS.ZOOM_MAX > LENS.ZOOM);
  assert.ok(Math.abs(LENS.R_PX - 0.0676 * 1920) < 1, "86.5 of 1280 px -> 130 stage px");
  assert.ok(LENS.RING_K > 0.1 && LENS.RING_K < 0.15 && LENS.HANDLE_K[1] > 1);
  assert.ok(LENS.IN_S < LENS.OUT_S + 0.1 && LENS.EDGE_MAX < 0.5);
  assert.equal(lensZoom({}), 1);
  assert.equal(lensZoom({ zoom: 2 }), 2);
  assert.equal(lensZoom({ zoom: 99 }), LENS.ZOOM_MAX, "clamped to the grammar's ceiling");
  assert.equal(lensZoom({ zoom: 0.2 }), 1, "a glass never shrinks the line");
});

test("the clock: up on its word, rises, travels over the middle, leaves by its end; down outside", () => {
  assert.equal(lensPose(sp(), 9.99).on, false);
  assert.equal(lensPose(sp(), 12.51).on, false);
  const p0 = lensPose(sp(), 10);
  assert.ok(p0.on && p0.a === 0 && p0.rise === 1 && p0.u === 0, "on its word: still below, not yet visible");
  const up = lensPose(sp(), 10 + LENS.IN_S);
  assert.ok(near(up.a, 1) && near(up.rise, 0) && up.u === 0, "risen: fully up, on its first stand");
  const mid = lensPose(sp(), 10 + LENS.IN_S + (2.5 - LENS.IN_S - LENS.OUT_S) / 2);
  assert.ok(near(mid.u, 0.5, 1e-9), "min-jerk: half the travel's clock is half the stretch");
  const trav = lensPose(sp(), 12.5 - LENS.OUT_S);
  assert.ok(near(trav.u, 1) && trav.exit === 0 && near(trav.a, 1), "the stretch is walked before it leaves");
  const gone = lensPose(sp(), 12.5);
  assert.ok(gone.on && near(gone.a, 0) && near(gone.exit, 1), "gone by the word's end");
  const short = lensPose(sp({ dur: 0.5 }), 10 + 0.5 * LENS.EDGE_MAX);
  assert.ok(near(short.a, 1), "a short word: the rise takes at most EDGE_MAX of it");
});

test("the stand is ON the series: the datum, or the stretch's head by length", () => {
  const E = line();
  assert.deepEqual(lensStand(E, 3, undefined, 0.7), E[3].p, "no `to`: it stands on `from`");
  assert.deepEqual(lensStand(E, 3, 6, 0), E[3].p);
  assert.deepEqual(lensStand(E, 3, 6, 1), E[6].p);
  const h = lensStand(E, 3, 6, 0.5);
  assert.ok(h[0] > E[3].p[0] && h[0] < E[6].p[0], "half way along by length");
  assert.deepEqual(lensStand(E, 6, 3, 0), E[6].p, "`from` > `to` runs the other way");
  assert.equal(lensStand(E.filter((q) => q.i !== 6), 3, 6, 0.5), null, "an edge the window dropped: no stand");
  assert.equal(lensStand(E, 42, undefined, 0), null);
});

test("inside the glass every vertex IS a datum, magnified about the centre; nothing past the pen; nothing invented", () => {
  const E = line(), c = E[5].p, k = 2;
  const m = lensMagnify(E, c, k, 60, null);
  const mapped = E.map((q) => [c[0] + k * (q.p[0] - c[0]), c[1] + k * (q.p[1] - c[1])]);
  assert.ok(m.length >= 3);
  for (const v of m) assert.ok(mapped.some((w) => near(w[0], v[0]) && near(w[1], v[1])), "a vertex no datum makes");
  assert.deepEqual(m[0], mapped[3], "one datum past the near edge, so the line runs out of the ring");
  assert.deepEqual(m[m.length - 1], mapped[7]);
  const one = lensMagnify(E, c, 1, 60, null);
  assert.deepEqual(one, E.slice(3, 8).map((q) => q.p), "zoom 1: the page's own points, where they are (Bravos's glass)");
  const pen = lensMagnify(E, c, k, 60, E[5].p[0] + 10);
  assert.ok(pen.every((v) => mapped.slice(0, 6).some((w) => near(w[0], v[0]) && near(w[1], v[1]))), "the pen stopped at 5");
  assert.equal(lensMagnify(E, [2000, 300], 2, 60, null), null, "nothing near the glass: nothing drawn");
});

test("the parts: the clip inside the ring, the neck and the handle straight down under it", () => {
  const P = lensParts([500, 300], 100);
  assert.ok(near(P.inner, 100 * (1 - LENS.RING_K)) && near(P.ringR + P.sw / 2, 100), "the ring's outer edge is R");
  assert.ok(near(P.neck.x + P.neck.w / 2, 500) && near(P.handle.x + P.handle.w / 2, 500), "straight down");
  assert.ok(P.neck.y > 300 + P.inner && near(P.handle.y, P.neck.y + P.neck.h) && near(P.handle.h, 100 * LENS.HANDLE_K[1]));
});

const rec = () => { const a = {}; return { a, setAttribute: (k, v) => { a[k] = String(v); } }; };
const built = (o = {}) => ({ sp: sp(o), si: 0, zoom: lensZoom(sp(o)), r: 40, g: rec(), clip: rec(), disc: rec(), ring: rec(),
                             neck: rec(), handle: rec(), lines: [{ si: 0, path: rec() }, { si: 1, path: rec() }] });

test("the painter reaches the page only through ctx: it stands the glass on the data and draws the magnified ink", () => {
  const E0 = line(), E1 = line().map((q) => ({ i: q.i, p: [q.p[0], q.p[1] + 80] }));
  const ctx = { pointsNow: (st, si) => (si === 0 ? E0 : E1) };
  const ld = built({ zoom: 2 });
  paintLens(ld, 9.9, {}, ctx);
  assert.equal(ld.g.a.opacity, "0", "before its word: down");
  paintLens(ld, 10 + LENS.IN_S, {}, ctx);
  assert.equal(ld.g.a.opacity, "1.000");
  assert.equal(+ld.ring.a.cx, E0[3].p[0]);
  assert.equal(+ld.ring.a.cy, E0[3].p[1]);
  assert.ok(ld.lines[0].path.a.d.startsWith("M"), "the named series, magnified");
  assert.ok(ld.lines[1].path.a.d.startsWith("M"), "... and the page's other drawn series with it (nothing vanishes under the glass)");
  const a = +ld.ring.a.cx;
  paintLens(ld, 11.3, {}, ctx);
  assert.ok(+ld.ring.a.cx > a, "it TRAVELS the stretch (s99)");
  paintLens(ld, 13, {}, ctx);
  assert.equal(ld.g.a.opacity, "0", "after its word: gone");
  const lost = built();
  paintLens(lost, 11, {}, { pointsNow: () => [] });
  assert.equal(lost.g.a.opacity, "0", "no data: no glass");
});
