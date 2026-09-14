// P57 T12 / R26-70b - THE COMPARE (E76: the quoted metric becomes the number the viewer feels). These tests pin the
// PURE FUNCTION the paint is: the two ends are the AUTHORED strings exactly, the numeral between them is monotone on
// min-jerk, two calls at one u give the same answer to the character, and nothing on screen is a number the row did
// not author. The last tests call the PAINTER itself on recorders with no DOM - it reaches the engine only through
// its ctx, so `el` is a recorder and the figure is the shape paintFigure's records carry.
import { test } from "node:test";
import assert from "node:assert/strict";
import { COMPARE, compareSplit, compareFmt, compareFrame, compareCapacity, compareGlyph, compareFigure,
         compareWidth, compareEnsure, compareInk, compareFill, paintCompare } from "../../scripts/species/compare.mjs";

/* the acceptance row (test_metric_comparator.py's own): a P/E of 24.8x against a 21.5x history, "15 % dearer" */
const row = (o = {}) => Object.assign({
  kind: "chart_to", at: 32.0, dur: 1.2, to: "compare",
  metric: { value: 24.8, text: "24.8x", label: "forward P/E" },
  comparator: { value: 0.1535, text: "15 % dearer", label: "dearer than its own history" },
  inputs: { pe: 24.8, hist: 21.5 }, derive: "pe / hist - 1",
  source: "[DERIVED: from ev-meta-pe-v1 + the 10-year median, pe / hist - 1]",
}, o);

test("the dials are the compare's, and every one of them is a share or a room", () => {
  assert.ok(COMPARE.COUNT > 0 && COMPARE.COUNT <= 1, "the count is a share of the window");
  assert.ok(COMPARE.SWAP > 0 && COMPARE.SWAP < 1 && COMPARE.LABEL_AT > COMPARE.SWAP, "the label is written after the swap");
  assert.ok(COMPARE.GHOST_A > 0 && COMPARE.GHOST_A < 1 && COMPARE.GHOST_F > 0 && COMPARE.GHOST_F < 1,
            "the held metric is the quieter and the smaller of the two");
  assert.equal(Object.isFrozen(COMPARE), true);
});

// ---------------------------------------------------------------- the text, split at its numeral
test("a text is PARTITIONED at its first numeral - pre + num + post is the string it came from", () => {
  for (const s of ["24.8x", "15 % dearer", "$1,240 a year", "-3.5 pp", "no number here", ""]) {
    const P = compareSplit(s);
    assert.equal(P.pre + P.num + P.post, s, s);
  }
  const m = compareSplit("24.8x");
  assert.deepEqual([m.pre, m.num, m.post, m.dec, m.group], ["", "24.8", "x", 1, false]);
  const c = compareSplit("15 % dearer");
  assert.deepEqual([c.pre, c.num, c.post, c.dec, c.group], ["", "15", " % dearer", 0, false]);
  const d = compareSplit("$1,240 a year");
  assert.deepEqual([d.pre, d.num, d.post, d.dec, d.group, d.value], ["$", "1,240", " a year", 0, true, 1240]);
  assert.ok(Number.isNaN(compareSplit("no number here").value), "a text with no numeral quotes no number");
});

test("a counted value wears the end's own clothes, and a sign only when it is one", () => {
  assert.equal(compareFmt(24.8, 1, false), "24.8");
  assert.equal(compareFmt(1240.4, 0, true), "1,240");
  assert.equal(compareFmt(-0.004, 2, false), "0.00", "a count through -0.004 must not flash a minus");
  assert.equal(compareFmt(-3.5, 1, false), "-3.5");
  assert.equal(compareFmt(NaN, 1, false), "");
});

// ---------------------------------------------------------------- the ends are the authored strings
test("u = 0 is the metric EXACTLY and u = 1 the comparator EXACTLY - the ends are the authored strings", () => {
  const sp = row();
  assert.equal(compareFrame(sp, 0).text, "24.8x");
  assert.equal(compareFrame(sp, 1).text, "15 % dearer");
  assert.equal(compareFrame(sp, -3).text, "24.8x", "before the word, the page is the page");
  assert.equal(compareFrame(sp, 4).text, "15 % dearer", "after it, the comparator holds");
  assert.equal(compareFrame(sp, 0).value, 24.8);
  assert.equal(compareFrame(sp, 1).value, 15);
  assert.equal(compareFrame(sp, 0).affix, 1);
  assert.equal(compareFrame(sp, 1).affix, 1);
  assert.equal(compareFrame(sp, 0).ghost, 0, "nothing is held beside the metric before it becomes anything");
});

test("the numeral counts between the two QUOTED numerals, never between the authored values (E77)", () => {
  const sp = row();
  for (let i = 0; i <= 40; i++) {
    const F = compareFrame(sp, i / 40);
    assert.ok(F.value <= 24.8 + 1e-9 && F.value >= 15 - 1e-9,
              `the count never leaves [15, 24.8] - it is 0.1535 that is the arithmetic, not the paint (u=${i / 40}, v=${F.value})`);
  }
});

test("the count is MONOTONE in u, and still at the ends (min-jerk)", () => {
  const sp = row();
  let prev = compareFrame(sp, 0).value;
  for (let i = 1; i <= 200; i++) {
    const v = compareFrame(sp, i / 200).value;
    assert.ok(v <= prev + 1e-12, `the number never goes back up (u=${i / 200})`);
    prev = v;
  }
  const d0 = compareFrame(sp, 0.002).value - compareFrame(sp, 0).value;
  assert.ok(Math.abs(d0) < 1e-3, "min-jerk leaves at rest");
  assert.equal(compareFrame(sp, COMPARE.COUNT).value, 15, "the count LANDS at COUNT of the window and holds");
  assert.equal(compareFrame(sp, 0.9).value, 15);
});

test("TWO CALLS AT ONE u GIVE THE SAME ANSWER - the frame is a pure function of u (a cold seek is the play)", () => {
  const sp = row();
  for (const u of [0, 0.137, 0.25, COMPARE.SWAP, 0.5001, 0.7, 0.9999, 1]) {
    assert.deepEqual(compareFrame(sp, u), compareFrame(sp, u), `u=${u}`);
    assert.deepEqual(compareFrame(row(), u), compareFrame(row(), u), `a fresh row at u=${u}`);
  }
});

test("the affix crosses THROUGH ZERO at the swap, so no character is ever cut", () => {
  const sp = row();
  assert.ok(Math.abs(compareFrame(sp, COMPARE.SWAP).affix) < 1e-9, "the words are at zero exactly where they change");
  assert.ok(compareFrame(sp, COMPARE.SWAP - 0.02).affix > 0);
  assert.ok(compareFrame(sp, COMPARE.SWAP + 0.02).affix > 0);
  const before = compareFrame(sp, COMPARE.SWAP - 0.02), after = compareFrame(sp, COMPARE.SWAP + 0.02);
  assert.ok(before.text.endsWith("x"), "the metric's clothes until the swap: " + before.text);
  assert.ok(after.text.endsWith(" % dearer"), "the comparator's after it: " + after.text);
  assert.equal(before.text.slice(before.i0, before.i1), compareFmt(before.value, 1, false), "the numeral's span is the numeral");
  assert.equal(after.text.slice(after.i0, after.i1), compareFmt(after.value, 0, false));
});

test("the label is written after the swap, the held metric arrives with it", () => {
  const sp = row();
  assert.equal(compareFrame(sp, COMPARE.LABEL_AT).sub, 0);
  assert.equal(compareFrame(sp, 1).sub, 1);
  assert.ok(compareFrame(sp, 0.8).sub > 0 && compareFrame(sp, 0.8).sub < 1);
  assert.equal(compareFrame(sp, 1).ghost, COMPARE.GHOST_A);
  assert.equal(compareGlyph(0, 0, 5), 0);
  assert.ok(compareGlyph(1, 4, 5) > 1 - 1e-9, "the last glyph is fully in exactly when the write ends");
});

test("a row that quotes no number at either end cross-fades and counts nothing", () => {
  const sp = row({ metric: { value: 1, text: "rich", label: "the word" },
                   comparator: { value: 2, text: "dearer than ever", label: "what it means" } });
  const F = compareFrame(sp, 0.3);
  assert.equal(F.counts, false);
  assert.equal(F.value, null);
  assert.equal(F.text, "rich");
  assert.equal(compareFrame(sp, 0.7).text, "dearer than ever");
  assert.equal(compareFrame(sp, 1).text, "dearer than ever");
});

// ---------------------------------------------------------------- the room the count needs
test("the capacity holds both authored strings and the widest number between them", () => {
  const sp = row();
  const cap = compareCapacity(sp);
  assert.ok(cap >= "15 % dearer".length && cap >= "24.8x".length);
  for (let i = 0; i <= 100; i++) assert.ok(compareFrame(sp, i / 100).text.length <= cap, "no frame outgrows the room");
  const big = row({ metric: { value: 1240, text: "$1,240 a year", label: "the bill" },
                    comparator: { value: 3.4, text: "3.4 cups of coffee a week", label: "what it buys" } });
  const capB = compareCapacity(big);
  for (let i = 0; i <= 100; i++) assert.ok(compareFrame(big, i / 100).text.length <= capB, "and a grouped one does not either");
});

// ---------------------------------------------------------------- the painter, on recorders
const recorder = () => {
  const mk = (tag) => ({ tag, at: {}, text: "", kids: [],
    setAttribute(k, v) { this.at[k] = v; },
    getAttribute(k) { return this.at[k]; },
    set textContent(v) { this.text = v; },
    get textContent() { return this.text; } });
  const el = (tag, cls, parent, at) => { const e = mk(tag); for (const k in (at || {})) e.at[k] = at[k];
    if (parent) parent.kids.push(e); return e; };
  return { el, mk };
};

const figureFor = (text, R) => {
  const g = R.mk("g"), label = R.mk("text");
  const lg = [...text].map(() => { const ts = R.mk("tspan"); label.kids.push(ts); return ts; });
  return { sp: { kind: "figure", at: 30, dur: 2, text }, g, label, lg, sub: null, sg: [],
           x: 500, y: 300, fits: true, fs: 28, fss: 17, si: 0, idx: 5 };
};

test("the painter finds the figure the page WROTE, by its text, and paints nothing without one", () => {
  const R = recorder(), fg = figureFor("24.8x", R);
  assert.equal(compareFigure([fg], row()), fg);
  assert.equal(compareFigure([figureFor("21.5x", R)], row()), null, "a figure quoting another number is another figure");
  assert.equal(compareFigure([], row()), null);
  assert.equal(compareFigure([fg], row({ metric: { value: 1, text: "  ", label: "x" } })), null);
  paintCompare({ sp: row(), figures: [] }, 32.6, {}, { el: R.el });   // and it does not throw on a page that lost it
});

test("THE PAINT AT ONE t IS THE PAINT AT THAT t - the same cells, the same characters, the same ink", () => {
  const R = recorder(), sp = row(), ctx = { el: R.el };
  const read = (fg) => ({ chars: fg.__compare.cells.map((c) => c.text),
                          ink: fg.__compare.cells.map((c) => c.at.opacity),
                          ghost: fg.__compare.ghost.at.opacity, sub: fg.__compare.sg.map((c) => c.at.opacity) });
  for (const t of [31.0, 32.3, 32.6, 32.9, 33.2, 40.0]) {
    const cold = figureFor("24.8x", R);                       // a COLD SEEK: one frame, straight to t
    paintCompare({ sp, figures: [cold] }, t, {}, ctx);
    const played = figureFor("24.8x", R);                     // a PLAY: every frame from before the word to t
    for (let k = 0; k <= 30; k++) paintCompare({ sp, figures: [played] }, 31.4 + (t - 31.4) * k / 30, {}, ctx);
    assert.deepEqual(read(cold), read(played), `a cold seek to ${t} lands where the play does`);
    assert.deepEqual(read(cold), (paintCompare({ sp, figures: [cold] }, t, {}, ctx), read(cold)), "and painting it twice changes nothing");
  }
});

test("the ends on the page: the metric before the word, the comparator and its label after", () => {
  const R = recorder(), sp = row(), ctx = { el: R.el }, fg = figureFor("24.8x", R);
  paintCompare({ sp, figures: [fg] }, 31.0, {}, ctx);
  assert.equal(fg.__compare.cells.slice(0, 5).map((c) => c.text).join(""), "24.8x");
  assert.equal(fg.__compare.ghost.at.opacity, "0.000", "nothing is held beside the figure before the word");
  assert.equal(fg.lg.every((c) => c.at.opacity === undefined), true, "and the figure's own hand still owns its glyphs");
  paintCompare({ sp, figures: [fg] }, 33.2, {}, ctx);
  assert.equal(fg.__compare.cells.map((c) => c.text).join("").replace(/ /g, " ").trim(), "15 % dearer");
  assert.equal(fg.__compare.ghost.at.opacity, COMPARE.GHOST_A.toFixed(3), "hold: metric (the default) keeps the quoted figure legible beside it");
  assert.equal(fg.__compare.ghost.text, "24.8x");
  assert.equal(fg.__compare.sg.map((c) => c.text).join("").replace(/ /g, " "), "dearer than its own history");
  assert.equal(fg.__compare.sg.every((c) => c.at.opacity === "1.000"), true, "the comparator's label is written by the end");
  const gone = figureFor("24.8x", R);
  paintCompare({ sp: row({ hold: "gone" }), figures: [gone] }, 33.2, {}, ctx);
  assert.equal(gone.__compare.ghost.at.opacity, "0.000", "hold: gone gives the comparator the stage");
});

test("the MIDDLE is a number in transition, not a cut", () => {
  const R = recorder(), sp = row(), ctx = { el: R.el }, fg = figureFor("24.8x", R);
  paintCompare({ sp, figures: [fg] }, 32.0 + 1.2 * 0.42, {}, ctx);
  const shown = fg.__compare.cells.map((c) => c.text).join("").replace(/ /g, " ").trim();
  assert.notEqual(shown, "24.8x");
  assert.notEqual(shown, "15 % dearer");
  assert.ok(/^\d+\.\dx$/.test(shown), "mid-window the page carries a number between the two, in the metric's clothes: " + shown);
  const v = parseFloat(shown);
  assert.ok(v < 24.8 && v > 15, "and it is on its way: " + v);
});

test("the held metric stands BESIDE the comparator - to the right where the figure fits, to the left where it does not", () => {
  const R = recorder(), sp = row(), ctx = { el: R.el };
  const right = figureFor("24.8x", R); paintCompare({ sp, figures: [right] }, 33.2, {}, ctx);
  const left = figureFor("24.8x", R); left.fits = false; paintCompare({ sp, figures: [left] }, 33.2, {}, ctx);
  assert.ok(+right.__compare.ghost.at.x > right.x, "the room is to the right: " + right.__compare.ghost.at.x);
  assert.ok(+left.__compare.ghost.at.x < left.x, "and to the left when the chart's edge is: " + left.__compare.ghost.at.x);
  assert.equal(right.__compare.ghost.at.y, (300).toFixed(1), "on the figure's own baseline - beside it, not over it");
  assert.equal(+right.__compare.sub.at.y > right.y, true, "the label is written beneath");
  assert.equal(compareWidth(null, "24.8x", 28), 5 * 28 * COMPARE.WIDTH_EM, "with no text metrics the width is the estimate");
});

test("compareEnsure builds once and GROWS - it never rebuilds what a frame already drew", () => {
  const R = recorder(), sp = row(), ctx = { el: R.el }, fg = figureFor("24.8x", R);
  const a = compareEnsure(fg, sp, ctx, 8), n0 = a.cells.length;
  const b = compareEnsure(fg, sp, ctx, 8);
  assert.equal(a, b, "the same bundle");
  assert.equal(b.cells.length, n0);
  assert.equal(b.cells[0], fg.lg[0], "the figure's own glyphs are the first cells - the number stays where the page wrote it");
  const c = compareEnsure(fg, sp, ctx, n0 + 3);
  assert.equal(c.cells.length, n0 + 3);
  assert.equal(c.ghost, a.ghost, "and nothing is built twice");
});

test("the ink is written as an INLINE STYLE as well - a class rule outranks a presentation attribute", () => {
  const R = recorder(), e = R.mk("text"); e.style = {};
  compareInk(e, COMPARE.GHOST_A);
  assert.equal(e.at.opacity, COMPARE.GHOST_A.toFixed(3));
  assert.equal(e.style.opacity, COMPARE.GHOST_A.toFixed(3), ".lp-chart .bksub carries opacity .85 - the attribute alone never lands");
  compareInk(e, -1); assert.equal(e.at.opacity, "0.000");
  compareInk(e, 7); assert.equal(e.at.opacity, "1.000");
  compareInk(null, 1);   // and a caller with nothing to ink does not throw
  assert.equal(compareFill({ label: { getAttribute: () => "font-size:28px;fill:var(--lp-chalk)" } }), "var(--lp-chalk)");
  assert.equal(compareFill({ label: { getAttribute: () => "font-size:28px;fill:#e8763a" } }), "#e8763a", "the figure's own accent, never a colour of ours");
  assert.equal(compareFill({}), "var(--lp-chalk)", "a figure with no style written is chalk");
});
