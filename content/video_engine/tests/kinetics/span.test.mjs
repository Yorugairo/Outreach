// P50 T4 - THE SPAN (R26-25; Bravos 107-110's "Decades"). A stretch of TIME shaded behind a ledger page's chart
// with its NAME above it. These tests pin the two edges (a datum index or an x-fraction), the band on the live
// points, the clock, and the fact that an edge the window has dropped names nothing and draws nothing (R26-28).
// P52 T5 (R26-41): THE PAINTER lives here too, registered into the PAGE registry, so the last test calls it on
// recorders with no DOM - it reaches the engine's perform layer only through its ctx.
import { test } from "node:test";
import assert from "node:assert/strict";
import * as SPAN_MOD from "../../scripts/species/span.mjs";
import { SPAN, spanIsIndex, spanEdgeX, spanExtent, spanBand, spanLabelY, spanPose, spanGlyph, paintSpan,
         spanToneIsDark, spanGround, spanAlphaOf } from "../../scripts/species/span.mjs";

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

// ---------------------------------------------------------------- the tone and its depth (E99 s46)
test("THE DEFAULT is the DARK span at 0.30 - the operator's own numbers, pinned here (E99 s46)", () => {
  assert.equal(SPAN.TONE, "dark", "E99 s46: 'yes' to the dark span - a span whose build names no tone is dark");
  assert.equal(SPAN.ALPHA_DARK, 0.30, "... at 0.30, the depth ruled with it");
  assert.equal(SPAN.ALPHA, 0.16, "and the LIGHT tone keeps its own law - chalk at 0.30 is the washed-out region s7 refused");
});

test("the tone is resolved in ONE place: absence and nonsense take the default, `light` is kept by name", () => {
  for (const absent of [undefined, null, ""]) assert.equal(spanToneIsDark(absent), true, JSON.stringify(absent));
  assert.equal(spanToneIsDark("dark"), true);
  assert.equal(spanToneIsDark("light"), false, "a build that says light gets the chalk wash it always had");
  assert.equal(spanToneIsDark("murky"), true, "an unknown value is not a third tone - it is the default");
  assert.equal(spanGround(undefined, "var(--lp-chalk)"), SPAN.DARK, "the ground darkens ...");
  assert.equal(spanGround("light", "var(--lp-chalk)"), "var(--lp-chalk)", "... unless the build asked for its colour");
});

test("the settled depth is the build's number, else the TONE's own law", () => {
  assert.equal(spanAlphaOf({}), SPAN.ALPHA_DARK, "no dial at all is the ruled default");
  assert.equal(spanAlphaOf({ tone: "light" }), SPAN.ALPHA, "the light tone stays at the law it was tuned at");
  assert.equal(spanAlphaOf({ alpha: 0.42, tone: "light" }), 0.42, "a number the build hands down wins either way");
  assert.equal(spanAlphaOf({ alpha: 0, tone: "light" }), SPAN.ALPHA, "a zero is a MISSING shade, not a darker one");
  assert.equal(spanAlphaOf({ alpha: -1 }), SPAN.ALPHA_DARK);
  assert.equal(spanAlphaOf({ alpha: "0.5" }), 0.5);
  assert.equal(spanAlphaOf({ alpha: 4 }), 1, "1 is an opacity's ceiling");
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
                                 height: band.h.toFixed(1), "fill-opacity": SPAN.ALPHA_DARK.toFixed(3) });
  assert.equal(sd.rect.at.x, "180.0");
  assert.equal(sd.rect.at["fill-opacity"], "0.300", "the shade is in at the DEFAULT depth - E99 s46's dark span at 0.30");
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

// ---------------------------------------------------------------- P72 T46g (R26-407): the BOX form (Bravos A56)
// A56 (BOOM 17:55.5-17:58.5, VERIFY.md's rescope): a dashed box round the LATEST ACTUAL stretch's own ink - the box
// names the move - which leaves, and then a dated rule names the date. `form` is the span's: `shade` (the default, every
// span before this slice) or `box`; anything else is refused by the compiler by name (R26-307's class).
const { SPAN_FORMS, SPAN_BOX, spanIsBox, spanStretch, spanBoxPose, spanBoxPath } = SPAN_MOD;

test("A56: the span has TWO forms, the shade the default, and the box's dials are its own", () => {
  assert.deepEqual([...SPAN_FORMS], ["shade", "box"]);
  assert.equal(spanIsBox({ form: "box" }), true);
  for (const f of [undefined, "shade", "zzz", null]) assert.equal(spanIsBox({ form: f }), false, String(f));
  assert.ok(SPAN_BOX.PAD > 0 && SPAN_BOX.DRAW_S > 0 && SPAN_BOX.LEAVE_S > 0 && SPAN_BOX.WIDTH > 0);
  assert.match(SPAN_BOX.DASH, /^\d+(\.\d+)? \d+(\.\d+)?$/, "a dashed box, as Bravos draws it");
});

test("A56: the box bounds the NAMED series' own ink over the stretch - not every series, not the plot", () => {
  const a = line(11, 0, 100, 600, (j) => 300 - 10 * j);          /* the named series: 300 -> 200 */
  const b = line(11, 0, 100, 600, () => 40);                      /* another line far above: not the box's */
  const r = spanStretch(a, 6, 10, SPAN_BOX.PAD, 560);
  assert.ok(r, "a stretch the window carries is boxed");
  assert.ok(near(r.x, 400 - SPAN_BOX.PAD) && near(r.x + r.w, 600 + SPAN_BOX.PAD), JSON.stringify(r));
  assert.ok(near(r.y, 200 - SPAN_BOX.PAD) && near(r.y + r.h, 240 + SPAN_BOX.PAD), "the stretch's own min..max: " + JSON.stringify(r));
  assert.ok(r.y > 40, "the other series never widens the box");
  void b;
  /* a fraction edge between two data takes the line's own value there (the ink the eye sees), not the next datum's */
  const f = spanStretch(a, 0.55, 0.95, 0, 560);   /* (1.0 would be the datum INDEX 1: an integer edge is an index) */
  assert.ok(near(f.x, 375) && near(f.x + f.w, 575) && near(f.y, 205) && near(f.y + f.h, 245), JSON.stringify(f));
  /* clipped to the chart's own box */
  const c = spanStretch(line(5, 0, 100, 500, (j) => (j === 4 ? 5 : 300)), 3, 4, SPAN_BOX.PAD, 560);
  assert.equal(c.y, 0);
});

test("A56: the box's right edge stops short of a page label past the stretch's end - never inside the stretch", () => {
  const a = line(11, 0, 100, 600, (j) => 300 - 10 * j);           /* the stretch 6..10 ends at x 600, y 200 */
  const free = spanStretch(a, 6, 10, SPAN_BOX.PAD, 560, [], 26);
  assert.ok(near(free.x + free.w, 600 + SPAN_BOX.PAD));
  const tag = { x: 610, y: 205 };                                 /* the series' own end tag, 10 units past its last datum */
  const r = spanStretch(a, 6, 10, SPAN_BOX.PAD, 560, [tag], 26);
  assert.ok(near(r.x + r.w, 610 - SPAN_BOX.LABEL_GAP), JSON.stringify(r));
  assert.ok(near(r.x, free.x) && near(r.y, free.y) && near(r.h, free.h), "only the right edge yields");
  assert.ok(near(spanStretch(a, 6, 10, SPAN_BOX.PAD, 560, [{ x: 601, y: 205 }], 26).x + spanStretch(a, 6, 10, SPAN_BOX.PAD, 560, [{ x: 601, y: 205 }], 26).w, 600),
            "a label hard on the tip: the edge stands ON the stretch's end, never inside it");
  assert.ok(near(spanStretch(a, 6, 10, SPAN_BOX.PAD, 560, [{ x: 610, y: 500 }], 26).w, free.w), "a label far below does not pull it");
  assert.ok(near(spanStretch(a, 6, 10, SPAN_BOX.PAD, 560, [{ x: 300, y: 205 }], 26).w, free.w), "a label before the stretch's end does not");
});

test("A56: an edge the window dropped boxes nothing, and two adjacent data are not a stretch", () => {
  assert.equal(spanStretch(line(41, 60), 10, 70, SPAN_BOX.PAD, 560), null, "R26-28: nothing to name, nothing drawn");
  assert.equal(spanStretch(line(3, 0, 100, 102), 0, 2, SPAN_BOX.PAD, 560), null, "narrower than MIN_W");
  assert.equal(spanStretch([], 0, 2, SPAN_BOX.PAD, 560), null);
});

test("A56: the box DRAWS round on its word, holds, and LEAVES over the end of its own dur", () => {
  const s = sp({ form: "box", at: 10, dur: 3 });
  assert.equal(spanBoxPose(s, 9.99).on, false);
  const p0 = spanBoxPose(s, 10);
  assert.equal(p0.on, true); assert.equal(p0.draw, 0); assert.equal(p0.fade, 1);
  assert.ok(near(spanBoxPose(s, 10 + SPAN_BOX.DRAW_S / 2).draw, 0.5));
  assert.equal(spanBoxPose(s, 10 + SPAN_BOX.DRAW_S).draw, 1);
  assert.equal(spanBoxPose(s, 13 - SPAN_BOX.LEAVE_S - 0.01).fade, 1, "it stands until its leave begins");
  assert.ok(near(spanBoxPose(s, 13 - SPAN_BOX.LEAVE_S / 2).fade, 0.5));
  assert.equal(spanBoxPose(s, 13).fade, 0, "gone at at + dur - the dated rule's turn (A56)");
  assert.equal(spanBoxPose(s, 20).fade, 0);
  /* a seek is the play */
  assert.deepEqual(spanBoxPose(s, 11.3), spanBoxPose(s, 11.3));
});

test("A56: the box's outline is drawn ROUND by length - the top, the right, the bottom, the left - and closes", () => {
  const r = { x: 100, y: 50, w: 200, h: 100 };                     /* perimeter 600 */
  assert.equal(spanBoxPath(r, 0), "", "nothing before the pen moves");
  assert.equal(spanBoxPath(r, 1 / 6), "M100.0 50.0 L200.0 50.0", "a sixth of the way: half the top");
  assert.equal(spanBoxPath(r, 0.5), "M100.0 50.0 L300.0 50.0 L300.0 150.0", "half: the top and the right, to the corner");
  assert.equal(spanBoxPath(r, 1), "M100.0 50.0 L300.0 50.0 L300.0 150.0 L100.0 150.0 L100.0 50.0 Z", "whole, and closed");
  assert.equal(spanBoxPath(r, 2), spanBoxPath(r, 1));
  assert.equal(spanBoxPath(null, 1), "");
});

test("A56: the PAINTER draws the box as ink ON the page - never a shade, never sunk to the ground", () => {
  const rec = () => ({ at: {}, setAttribute(k, v) { this.at[k] = v; } });
  const pts = line(101);
  const mk = (o = {}) => {
    const sd = { sp: sp(Object.assign({ form: "box", at: 8, dur: 3, from: 60, to: 90 }, o)), si: 0, rect: rec(), label: rec(),
                 lg: [], fs: 26, box: rec() };
    const st = { linePts: [pts], geom: { H: 560 } };
    return { sd, st, ctx: { pointsNow: () => pts } };
  };
  let { sd, st, ctx } = mk();
  paintSpan(sd, 7.9, st, ctx);
  assert.equal(sd.box.at.opacity, 0); assert.equal(sd.rect.at["fill-opacity"], 0);
  ({ sd, st, ctx } = mk());
  paintSpan(sd, 8 + SPAN_BOX.DRAW_S + 0.5, st, ctx);
  const r = spanStretch(pts, 60, 90, SPAN_BOX.PAD, 560);
  assert.equal(sd.box.at.d, spanBoxPath(r, 1), "the whole box, round the stretch");
  assert.equal(sd.box.at.opacity, "1.000");
  assert.equal(sd.rect.at["fill-opacity"], 0, "a box is not a shade: the ground stays untouched");
  assert.equal(sd.rect.at.x, undefined);
  assert.equal(sd.label.at.opacity, 0, "a box with no name writes nothing");
  ({ sd, st, ctx } = mk());
  paintSpan(sd, 11.5, st, ctx);
  assert.equal(sd.box.at.opacity, 0, "after its dur the box has left");
  /* a NAMED box writes its name over the box's own top, glyph by glyph, and leaves with it */
  ({ sd, st, ctx } = mk());
  sd.lg = Array.from({ length: 4 }, rec);
  paintSpan(sd, 8 + SPAN_BOX.DRAW_S + 3 * SPAN.WRITE, st, ctx);
  assert.equal(sd.label.at.y, spanLabelY({ yTop: r.y, y: r.y }, sd.fs).toFixed(1));
  assert.equal(sd.label.at.x, (r.x + r.w / 2).toFixed(1));
  assert.deepEqual(sd.lg.map((g) => g.at.opacity), ["1.000", "1.000", "1.000", "1.000"]);
});
