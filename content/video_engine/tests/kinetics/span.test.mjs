// P50 T4 - THE SPAN (R26-25; Bravos 107-110's "Decades"). A stretch of TIME shaded behind a ledger page's chart
// with its NAME above it. These tests pin the two edges (a datum index or an x-fraction), the band on the live
// points, the clock, and the fact that an edge the window has dropped names nothing and draws nothing (R26-28).
// P52 T5 (R26-41): THE PAINTER lives here too, registered into the PAGE registry, so the last test calls it on
// recorders with no DOM - it reaches the engine's perform layer only through its ctx.
import { test } from "node:test";
import assert from "node:assert/strict";
import { SPAN, spanIsIndex, spanEdgeX, spanExtent, spanBand, spanLabelY, spanPose, spanGlyph, paintSpan } from "../../scripts/species/span.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
/* lpPointsNow's own shape: the PAGE's datum index and the point in the chart's viewBox */
const line = (n, off = 0, x0 = 100, x1 = 900, y = (i) => 300 - i) =>
  Array.from({ length: n }, (_, j) => ({ i: off + j, p: [x0 + (x1 - x0) * j / (n - 1), y(j)] }));
const sp = (o = {}) => Object.assign({ kind: "span", at: 8, dur: 8, from: 10, to: 60, label: "THE DECADE" }, o);

test("the dials are the span's, and the shade never fights the line it stands behind", () => {
  assert.ok(SPAN.IN_S > 0 && SPAN.WRITE > 0 && SPAN.WRITE <= 1);
  assert.ok(SPAN.ALPHA > 0 && SPAN.ALPHA < 0.3, "a span is the room the argument happens in, not the argument");
  assert.ok(SPAN.PAD_T > 0 && SPAN.PAD_B > 0 && SPAN.MIN_W > 0);
});

// ---------------------------------------------------------------- the two edges
test("an INTEGER edge is a datum index; anything else is an x-fraction of the drawn series", () => {
  assert.equal(spanIsIndex(7), true);
  assert.equal(spanIsIndex(0), true);
  assert.equal(spanIsIndex(0.5), false);
  assert.equal(spanIsIndex(1.0), true, "1.0 IS 1 in a JSON number - the compiler is what keeps the two apart");
  const pts = line(101);
  assert.ok(near(spanEdgeX(pts, 0), 100));
  assert.ok(near(spanEdgeX(pts, 100), 900));
  assert.ok(near(spanEdgeX(pts, 50), 500), "the index resolves to the point that carries it, not to a length");
  assert.ok(near(spanEdgeX(pts, 0.25), 300), "a fraction runs along the series' own x extent");
  assert.ok(near(spanEdgeX(pts, 0.0), 100) && near(spanEdgeX(pts, 1.5), 900), "and is clamped to it");
});

test("an index the window has DROPPED names nothing - the band is not drawn in the wrong place (R26-28)", () => {
  const windowed = line(41, 60);            // a rescale left indices 60..100 on screen
  assert.equal(spanEdgeX(windowed, 10), null, "index 10 is off the window");
  assert.ok(near(spanEdgeX(windowed, 60), 100));
  assert.equal(spanEdgeX([], 3), null);
  assert.equal(spanEdgeX([{ i: 0, p: [1, 2] }], 0), null, "one point is not a series");
  assert.equal(spanEdgeX(null, 3), null);
  assert.equal(spanEdgeX(line(9), "soon"), null, "a fraction that is not a number names nothing");
  assert.equal(spanBand(windowed, [windowed], 10, 30, 560), null, "and the whole band goes with it");
});

// ---------------------------------------------------------------- the band
test("the band reaches over EVERY drawn series, padded, and is clipped to the chart's own box", () => {
  const a = line(101, 0, 100, 900, (j) => 300 - j), b = line(101, 0, 100, 900, (j) => 420 + j / 2);
  const ext = spanExtent([a, b]);
  assert.ok(near(ext.y0, 200 - SPAN.PAD_T), "the highest point of any series, padded up");
  assert.ok(near(ext.y1, 470 + SPAN.PAD_B), "the lowest, padded down");
  const band = spanBand(a, [a, b], 10, 60, 560);
  assert.ok(near(band.x, 180) && near(band.w, 400), "x from the NAMED series, the pair in order");
  assert.ok(near(band.cx, 380));
  assert.ok(near(band.y, 156) && near(band.y + band.h, 514));
  const clipped = spanBand(a, [a, b], 10, 60, 500);
  assert.ok(near(clipped.y + clipped.h, 500), "clipped to the chart's height, never drawn off the page");
  assert.equal(spanExtent([]), null);
  assert.equal(spanExtent([[]]), null);
});

test("the two edges may be given in either order, and a band with no width is not a span", () => {
  const a = line(101);
  const fwd = spanBand(a, [a], 10, 60, 560), back = spanBand(a, [a], 60, 10, 560);
  assert.deepEqual(back, fwd, "the band is the stretch between them, however they were named");
  assert.equal(spanBand(a, [a], 10, 10, 560), null, "a point is a bracket's business, not a span's");
  assert.equal(spanBand(a, [a], 0.5, 0.5005, 560), null, "... and so is a gap under MIN_W");
});

test("the NAME goes above the band, or inside its top edge when the chart fills its box", () => {
  const fs = 26;
  assert.ok(near(spanLabelY({ y: 200 }, fs), 200 - SPAN.LABEL_DY), "room above: the name stands over the band");
  const tight = spanLabelY({ y: 0 }, fs);
  assert.ok(tight > 0, "no room above: the name is written inside the band's top");
  assert.ok(near(tight, fs * SPAN.LABEL_IN));
  assert.ok(spanLabelY({ y: fs * SPAN.LABEL_ROOM }, fs) < fs * SPAN.LABEL_ROOM, "the boundary falls on the 'above' side");
});

// ---------------------------------------------------------------- the clock
test("the shade fades in over IN_S; the hand writes after it, over WRITE of the word", () => {
  const s = sp();
  const before = spanPose(s, s.at - 0.01);
  assert.deepEqual([before.on, before.shade, before.alpha, before.write], [false, 0, 0, 0]);
  assert.deepEqual([spanPose(s, s.at).on, spanPose(s, s.at).shade], [true, 0]);
  const half = spanPose(s, s.at + SPAN.IN_S / 2);
  assert.ok(near(half.shade, 0.5) && near(half.alpha, SPAN.ALPHA / 2));
  assert.equal(half.write, 0, "not a glyph until the shade is in");
  const inn = spanPose(s, s.at + SPAN.IN_S);
  assert.ok(near(inn.shade, 1) && near(inn.alpha, SPAN.ALPHA) && inn.write === 0);
  assert.ok(near(spanPose(s, s.at + SPAN.IN_S + s.dur * SPAN.WRITE / 2).write, 0.5));
  assert.ok(near(spanPose(s, s.at + SPAN.IN_S + s.dur * SPAN.WRITE).write, 1));
  const held = spanPose(s, s.at + 40);
  assert.deepEqual([held.shade, held.write], [1, 1], "it HOLDS: a span has no end event, it stands with the page");
});

test("the label is written glyph after glyph, in order, and never runs backwards", () => {
  const n = 10;
  assert.equal(spanGlyph(0, 0, n), 0);
  assert.ok(near(spanGlyph(1, n - 1, n), 1, 1e-12), "the last glyph is in exactly when the write ends");
  assert.ok(spanGlyph(0.99, n - 1, n) < 1, "... and not one beat before it");
  assert.ok(spanGlyph(0.5, 0, n) === 1 && spanGlyph(0.5, 9, n) === 0, "the head is in before the tail starts");
  for (let j = 0; j < n; j++) {
    let prev = -1;
    for (let w = 0; w <= 1.0001; w += 0.01) { const v = spanGlyph(w, j, n); assert.ok(v >= prev - 1e-12, `${j} ${w}`); prev = v; }
  }
  const empty = spanGlyph(0.5, 0, 0);
  assert.ok(Number.isFinite(empty) && empty >= 0 && empty <= 1, "an empty label divides by one, not by zero");
});

// ---------------------------------------------------------------- pure function of t
test("a seek IS the play: the same t gives the same bits, in any order, with nothing remembered", () => {
  const s = sp(), a = line(101);
  const read = (t) => JSON.stringify([spanPose(s, t), spanBand(a, [a], s.from, s.to, 560)]);
  const forward = [], backward = [];
  for (let i = 0; i <= 400; i++) forward.push(read(i / 25));
  for (let i = 400; i >= 0; i--) backward.unshift(read(i / 25));
  assert.deepEqual(backward, forward);
});

test("nothing in the module reaches for a clock or a random", () => {
  const src = [spanPose, spanBand, spanEdgeX, spanExtent, spanGlyph, spanLabelY].map((f) => f.toString()).join("\n");
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});

// ---------------------------------------------------------------- the painter, on recorders
test("THE PAINTER paints the band and the name through its ctx, and nothing at all before its word", () => {
  const rec = () => ({ at: {}, setAttribute(k, v) { this.at[k] = v; } });
  const pts = line(101);
  const stub = (o = {}) => {
    const lg = Array.from({ length: 10 }, rec);
    const sd = { sp: sp(o.sp), si: 0, rect: rec(), label: rec(), lg, fs: 26 };
    const st = { linePts: [pts], geom: { H: 560 } };
    const ctx = { pointsNow: (state, i) => { assert.equal(state, st); return o.points === undefined ? pts : o.points; } };
    return { sd, st, ctx };
  };

  // before the span's own `at`: hidden, and not one number written
  let { sd, st, ctx } = stub();
  paintSpan(sd, sd.sp.at - 0.01, st, ctx);
  assert.deepEqual(sd.rect.at, { "fill-opacity": 0 });
  assert.deepEqual(sd.label.at, { opacity: 0 });

  // the shade in, the hand not yet writing: the band is the law's, to the law's own precision
  ({ sd, st, ctx } = stub());
  const t0 = sd.sp.at + SPAN.IN_S;
  paintSpan(sd, t0, st, ctx);
  const band = spanBand(pts, [pts], sd.sp.from, sd.sp.to, 560);
  assert.deepEqual(sd.rect.at, { x: band.x.toFixed(1), y: band.y.toFixed(1), width: band.w.toFixed(1),
                                 height: band.h.toFixed(1), "fill-opacity": SPAN.ALPHA.toFixed(3) });
  assert.equal(sd.rect.at.x, "180.0");
  assert.equal(sd.rect.at["fill-opacity"], "0.160", "the shade is in, and it is the dial's own alpha");
  assert.deepEqual(sd.label.at, { opacity: 1, x: band.cx.toFixed(1), y: spanLabelY(band, sd.fs).toFixed(1) });
  assert.equal(sd.label.at.y, "140.0", "the name stands over the band");
  assert.deepEqual(sd.lg.map((g) => g.at.opacity), sd.lg.map(() => "0.000"), "not a glyph until the shade is in");

  // the word over: every glyph in, in order
  ({ sd, st, ctx } = stub());
  paintSpan(sd, sd.sp.at + SPAN.IN_S + sd.sp.dur * SPAN.WRITE, st, ctx);
  assert.deepEqual(sd.lg.map((g) => g.at.opacity), sd.lg.map(() => "1.000"));

  // an edge the window has dropped: hidden, never drawn in the wrong place (R26-28)
  ({ sd, st, ctx } = stub({ points: line(41, 60) }));
  paintSpan(sd, sd.sp.at + 4, st, ctx);
  assert.equal(sd.rect.at["fill-opacity"], 0);
  assert.equal(sd.label.at.opacity, 0);
  assert.equal(sd.rect.at.x, undefined, "nothing to name, nothing moved");
});

test("the painter reaches the engine ONLY through ctx - no free identifier, no DOM, no clock of its own", () => {
  const src = paintSpan.toString();
  assert.ok(/ctx\.pointsNow\(/.test(src), "the live points arrive by name");
  assert.ok(!/\blp[A-Z]/.test(src), "nothing the engine owns is reached as a free identifier: " + src);
  assert.ok(!/document\.|window\.|globalThis|Math\.random|Date\.now|performance\./.test(src),
    "no DOM and no clock of its own - the perform layer hands it both elements and t: " + src);
  assert.equal(typeof paintSpan, "function");
  assert.equal(paintSpan.length, 4, "paint(sd, t, st, ctx) - the page registry's own signature");
});
