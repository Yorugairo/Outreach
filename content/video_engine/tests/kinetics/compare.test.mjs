// P57 T12 / R26-70b - THE COMPARE (E76: the quoted metric becomes the number the viewer feels). These tests pin the
// PURE FUNCTION the paint is: the two ends are the AUTHORED strings exactly, the numeral between them is monotone on
// min-jerk, two calls at one u give the same answer to the character, and nothing on screen is a number the row did
// not author. The last tests call the PAINTER itself on recorders with no DOM - it reaches the engine only through
// its ctx, so `el` is a recorder and the figure is the shape paintFigure's records carry.
import { test } from "node:test";
import assert from "node:assert/strict";
import { COMPARE, COMPARE_FORMS, COMPARE_THENS, compareSplit, compareFmt, compareFrame, compareCapacity, compareGlyph,
         compareFigure, compareWidth, compareEnsure, compareInk, compareFill, paintCompare, compareForm, compareThen,
         compareMorphFrame, compareTakeGlyph, compareTakeFall, compareMeltBox, compareBallFrame, compareBallR,
         compareBallC, compareGroups, comparePairGroups, comparePrepare, comparePath, compareSagAt, compareRnd,
         compareSeed } from "../../scripts/species/compare.mjs";
import { FIGURE } from "../../scripts/species/figure.mjs";
import { MELT, meltDrips } from "../../scripts/species/melt.mjs";
import { polyArea, centroid } from "../../scripts/kinetics/arap.mjs";

/* the acceptance row (test_metric_comparator.py's own): a P/E of 24.8x against a 21.5x history, "15 % dearer" */
const row = (o = {}) => Object.assign({
  kind: "chart_to", at: 32.0, dur: 1.2, to: "compare",
  metric: { value: 24.8, text: "24.8x", label: "forward P/E" },
  comparator: { value: 0.1535, text: "15 % dearer", label: "dearer than its own history" },
  inputs: { pe: 24.8, hist: 21.5 }, derive: "pe / hist - 1",
  source: "[DERIVED: from ev-meta-pe-v1 + the 10-year median, pe / hist - 1]",
}, o);

/* T12's counter, now a SETTING: the tests that pin the count's own law author it by name */
const countRow = (o = {}) => row(Object.assign({ form: "count" }, o));
/* ... and P57 T12b's text melt, which P57 T12c kept whole under the name `streak` when the DEFAULT became the ball */
const streakRow = (o = {}) => row(Object.assign({ form: "streak" }, o));

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

test("the MIDDLE of the COUNT form is a number in transition, not a cut", () => {
  const R = recorder(), sp = countRow(), ctx = { el: R.el }, fg = figureFor("24.8x", R);
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

// ---------------------------------------------------------------- P57 T12b: THE THREE FORMS (the operator's correction)
test("the form is MELT unless the row says otherwise, and an unknown one is refused BY NAME", () => {
  assert.deepEqual([...COMPARE_FORMS], ["melt", "streak", "collapse", "count"]);
  assert.equal(compareForm(row()), "melt", "the default is the operator's correction: the figure balls up");
  assert.equal(compareForm(streakRow()), "streak");
  assert.equal(compareForm(row({ form: "collapse" })), "collapse");
  assert.equal(compareForm(countRow()), "count");
  assert.throws(() => compareForm(row({ form: "morph" })), /form morph is not one of melt \| streak \| collapse \| count/,
                "`morph` is an ENDING, not a form - a row naming it as one is refused, never read as the other key");
  assert.throws(() => compareForm(row({ form: "" })), /is not one of/, "an empty form is a typo, not a default");
  assert.ok(COMPARE.TAKE_SHARE > 0 && COMPARE.TAKE_SHARE < 1, "the take-away is a share of the window");
});

test("THE ENDING is MORPH unless the row says otherwise, and an unknown one is refused BY NAME", () => {
  assert.deepEqual([...COMPARE_THENS], ["morph", "splash", "throw"]);
  assert.equal(compareThen(row()), "morph", "the operator's default: the ball becomes the comparator's glyphs");
  for (const t of COMPARE_THENS) assert.equal(compareThen(row({ then: t })), t);
  assert.throws(() => compareThen(row({ then: "melt" })), /then melt is not one of morph \| splash \| throw/);
  assert.throws(() => compareThen(row({ then: "" })), /is not one of/);
});

test("u = 0 is the metric and u = 1 the comparator FOR ALL FOUR FORMS - the ends are the authored strings", () => {
  for (const form of COMPARE_FORMS) {
    const sp = row({ form });
    const F = (u) => (form === "count" ? compareFrame(sp, u)
                    : form === "melt" ? compareBallFrame(sp, u, "morph") : compareMorphFrame(sp, u, form));
    assert.equal(F(0).text, "24.8x", form);
    assert.equal(F(1).text, "15 % dearer", form);
    assert.equal(F(-2).text, "24.8x", form + " - before the word, the page is the page");
    assert.equal(F(7).text, "15 % dearer", form + " - after it, the comparator holds");
  }
});

test("THE FOUR FORMS DIFFER AT ONE u - one row, four different pages mid-morph", () => {
  const R = recorder(), ctx = { el: R.el }, u = 0.3, t = 32.0 + 1.2 * u;
  const seen = COMPARE_FORMS.map((form) => {
    const fg = figureFor("24.8x", R);
    paintCompare({ sp: row({ form }), figures: [fg] }, t, {}, ctx);
    return { form, ink: fg.__compare.cells.map((c) => c.at.opacity).join(","),
             dy: fg.__compare.cells.map((c) => c.at.dy).join(","),
             text: fg.__compare.cells.map((c) => c.text).join("") };
  });
  const [ball, streak, collapse, count] = seen;
  assert.notEqual(streak.ink, collapse.ink, "the ink melts in the hand's reading order; the collapse takes it back last glyph first");
  assert.notEqual(streak.ink, count.ink, "and the counter never dims its numeral at all");
  assert.notEqual(streak.dy, collapse.dy, "only the streak RUNS: the collapse's glyphs never move");
  assert.equal(ball.ink.split(",").every((v) => v === "0.000"), true,
               "the BALL form takes the ink out of the <text> entirely - mid-window the glyphs are outlines, not type: " + ball.ink);
  assert.equal(count.dy.replace(/,/g, ""), "",
               "the COUNT form writes no dy at all - not one attribute of T12's paint changes, and its golden is byte-identical");
  assert.equal(count.text.replace(/\u00a0/g, " ").trim().endsWith("x"), true, "mid-count the page is still in the metric's clothes: " + count.text);
});

test("THE TAKE-AWAY ENDS BEFORE THE WRITE BEGINS - the last drop falls as the first glyph arrives", () => {
  for (const form of ["streak", "collapse"]) {
    const sp = row({ form });
    const at = compareMorphFrame(sp, COMPARE.TAKE_SHARE, form);
    assert.equal(at.take, 1, form + ": the take-away is whole exactly at TAKE_SHARE");
    assert.equal(at.write, 0, form + ": and the hand has not started");
    assert.equal(at.text, "24.8x", form + ": the quoted figure is still the string on the page");
    for (let i = 0; i <= 60; i++) {
      const u = i / 60, F = compareMorphFrame(sp, u, form);
      assert.ok(!(F.take < 1 && F.write > 0), form + ": the two never overlap (u=" + u + ")");
      assert.ok(F.take >= compareMorphFrame(sp, Math.max(0, u - 1 / 60), form).take - 1e-12, form + ": the take-away never goes back");
    }
    const n = 5;
    for (let j = 0; j < n; j++) {
      assert.equal(compareTakeGlyph(form, 0, j, n), 1, form + ": every glyph is whole before the take-away");
      assert.ok(compareTakeGlyph(form, 1, j, n) < 1e-9, form + ": and gone at the end of it");
    }
  }
  assert.equal(compareTakeFall("collapse", 0.5, 0, 5, 100), 0, "a collapse is the hand, not a liquid: nothing runs");
  assert.ok(compareTakeFall("streak", 1, 0, 5, 100) > 0, "a streak RUNS - melt.mjs's own run, on the room under the number");
  assert.equal(compareTakeFall("streak", 0, 0, 5, 100), 0);
  assert.ok(compareMeltBox(28) > (FIGURE.FIGURE_UP + FIGURE.FIGURE_DOWN) * 28, "the ink falls into the room under the figure, not into its own box");
});

test("TWO CALLS AT ONE u GIVE THE SAME ANSWER for the morph forms too (a cold seek is the play)", () => {
  for (const form of ["streak", "collapse"]) {
    for (const u of [0, 0.137, COMPARE.TAKE_SHARE, 0.56, 0.8, 0.9999, 1]) {
      assert.deepEqual(compareMorphFrame(row({ form }), u, form), compareMorphFrame(row({ form }), u, form), form + " u=" + u);
    }
  }
  const R = recorder(), ctx = { el: R.el };
  for (const form of ["streak", "collapse"]) {
    const sp = row({ form });
    const read = (fg) => ({ chars: fg.__compare.cells.map((c) => c.text), ink: fg.__compare.cells.map((c) => c.at.opacity),
                            dy: fg.__compare.cells.map((c) => c.at.dy), ghost: fg.__compare.ghost.at.opacity });
    for (const t of [31.0, 32.3, 32.66, 32.9, 33.2]) {
      const cold = figureFor("24.8x", R);
      paintCompare({ sp, figures: [cold] }, t, {}, ctx);
      const played = figureFor("24.8x", R);
      for (let k = 0; k <= 30; k++) paintCompare({ sp, figures: [played] }, 31.4 + (t - 31.4) * k / 30, {}, ctx);
      assert.deepEqual(read(cold), read(played), form + ": a cold seek to " + t + " lands where the play does");
    }
  }
});

test("the STREAK re-draws the comparator by the HAND, with its label beneath and the metric ghosted", () => {
  const R = recorder(), ctx = { el: R.el }, sp = streakRow(), fg = figureFor("24.8x", R);
  paintCompare({ sp, figures: [fg] }, 32.0 + 1.2 * 0.75, {}, ctx);   // mid-write
  const ink = fg.__compare.cells.map((c) => +c.at.opacity);
  assert.equal(fg.__compare.cells.map((c) => c.text).join("").replace(/\u00a0/g, " ").trim(), "15 % dearer",
               "the cells carry the comparator AS AUTHORED once the hand starts");
  const n = "15 % dearer".length;
  assert.ok(ink.slice(0, n).every((v, j, a) => j === 0 || v <= a[j - 1] + 1e-9), "the hand writes it left to right: " + ink.slice(0, n).join(" "));
  assert.ok(ink[0] === 1 && ink[n - 1] < 1, "its first letters are in and its last are still arriving: " + ink.slice(0, n).join(" "));
  assert.equal(fg.__compare.cells.every((c) => +c.at.dy === 0), true, "nothing is still falling once the ink has gone");
  paintCompare({ sp, figures: [fg] }, 33.2, {}, ctx);
  assert.equal(fg.__compare.cells.map((c) => c.text).join("").replace(/\u00a0/g, " ").trim(), "15 % dearer");
  assert.equal(fg.__compare.sg.every((c) => c.at.opacity === "1.000"), true, "the label lands whole, exactly as the window ends");
  assert.equal(fg.__compare.ghost.at.opacity, COMPARE.GHOST_A.toFixed(3), "and the quoted figure is held beside it");
  const gone = figureFor("24.8x", R);
  paintCompare({ sp: streakRow({ hold: "gone" }), figures: [gone] }, 33.2, {}, ctx);
  assert.equal(gone.__compare.ghost.at.opacity, "0.000");
});

test("the STREAK leaves the page as it stood before the word, and takes the ink DOWN over the take-away", () => {
  const R = recorder(), ctx = { el: R.el }, sp = streakRow(), fg = figureFor("24.8x", R);
  paintCompare({ sp, figures: [fg] }, 31.0, {}, ctx);
  assert.equal(fg.lg.every((c) => c.at.opacity === undefined), true, "before the word the figure's own hand owns its glyphs");
  assert.equal(fg.__compare.cells.every((c) => +c.at.dy === 0), true, "and nothing has moved");
  paintCompare({ sp, figures: [fg] }, 32.0 + 1.2 * 0.4, {}, ctx);
  const dy = fg.lg.map((c) => +c.at.dy);
  assert.ok(dy.some((v) => v > 0), "mid-melt the ink is running down: " + dy.join(" "));
  assert.ok(+fg.lg[0].at.opacity < 1, "the first drip opens first");
  assert.ok(+fg.lg[0].at.opacity <= +fg.lg[fg.lg.length - 1].at.opacity + 1e-9, "the drips open in the hand's reading order");
  assert.equal(fg.__compare.melt.id, "cmpmelt0-5", "the streak's filter is mounted once, under the figure's own datum");
});

// ---------------------------------------------------------------- P57 T12c: THE BALL (E76 s5)
/* a glyph as a BOX ring, which is all the pairing rule reads: an outer ring and its centroid */
const boxRing = (x, w, h = 10) => [[x, 0], [x + w, 0], [x + w, h], [x, h]];
const boxGroup = (x, w, holes = []) => ({ outer: boxRing(x, w), holes, c: centroid(boxRing(x, w)) });

test("the T12c dials are shares, rooms and scales - and the ball is never a speck", () => {
  assert.ok(COMPARE.RASTER_S >= 2, "the raster is drawn above the page's own scale");
  assert.ok(COMPARE.RASTER_A > 0 && COMPARE.RASTER_A < 1, "the threshold is a share of full ink");
  assert.ok(COMPARE.SIMPLIFY > 0 && COMPARE.DEGEN_R > 0 && COMPARE.BALL_SWELL > 0 && COMPARE.BALL_MIN > 0);
  assert.equal(Object.isFrozen(COMPARE), true);
});

test("THE PAIRING RULE on 24.8x -> 15 %: five glyphs to three, by rank, the surplus into its neighbour's destination", () => {
  /* the five glyphs of "24.8x" and the three of "15 %", as boxes in reading order */
  const A = [0, 10, 20, 26, 34].map((x) => boxGroup(x, 8));
  const B = [0, 14, 28].map((x) => boxGroup(x, 10));
  const pairs = comparePairGroups(A, B, COMPARE.DEGEN_R);
  assert.equal(pairs.length, 5, "every ring of the larger set is in exactly one pair");
  for (let i = 0; i < 3; i++) {
    assert.deepEqual(pairs[i].src, A[i].outer, "rank " + i + " pairs with rank " + i);
    assert.deepEqual(pairs[i].dst, B[i].outer);
    assert.ok(!pairs[i].dies && !pairs[i].born, "a paired ring is neither born nor dying");
  }
  for (const p of pairs.slice(3)) {
    assert.equal(p.dies, true, "the surplus glyphs COLLAPSE - nothing is born on this side");
    const c = centroid(p.dst);
    assert.ok(Math.abs(c[0] - B[2].c[0]) < 1e-6 && Math.abs(c[1] - B[2].c[1]) < 1e-6,
              "into a degenerate ring at the nearest paired neighbour's destination: " + c.join(","));
    assert.ok(Math.abs(polyArea(p.dst)) < Math.abs(polyArea(B[2].outer)) / 20, "and it is a ring of nothing: " + Math.abs(polyArea(p.dst)).toFixed(2));
  }
});

test("THE SAME RULE carries ONE ring into N - which is what the ball becoming the comparator IS", () => {
  const ball = [boxGroup(20, 12)], glyphs = [0, 14, 28].map((x) => boxGroup(x, 10));
  const pairs = comparePairGroups(ball, glyphs, COMPARE.DEGEN_R);
  assert.equal(pairs.length, 3);
  assert.deepEqual(pairs[0].src, ball[0].outer, "one glyph is carried out of the ball itself");
  assert.equal(pairs.filter((p) => p.born).length, 2, "and the rest are BORN from it");
  for (const p of pairs.filter((q) => q.born)) {
    const c = centroid(p.src);
    assert.ok(Math.abs(c[0] - ball[0].c[0]) < 1e-6, "every one of them out of the ball's own centre: " + c[0]);
  }
});

test("HOLES pair with HOLES inside a paired glyph, and a surplus hole closes into its own glyph", () => {
  const withHole = { outer: boxRing(0, 20, 20), holes: [boxRing(5, 10, 10)], c: centroid(boxRing(0, 20, 20)) };
  const plain = boxGroup(0, 20);
  const shut = comparePairGroups([withHole], [plain], COMPARE.DEGEN_R);
  assert.equal(shut.length, 2);
  assert.equal(shut[1].hole, true);
  assert.equal(shut[1].dies, true, "the ink fuses: a hole has nowhere to go but its own glyph's destination");
  const open = comparePairGroups([plain], [withHole], COMPARE.DEGEN_R);
  assert.equal(open[1].born, true, "and the other way round it opens");
  assert.equal(open[1].hole, true);
  const both = comparePairGroups([withHole], [withHole], COMPARE.DEGEN_R);
  assert.deepEqual(both.map((p) => p.hole), [false, true], "two glyphs with one hole each pair outer to outer, hole to hole");
  assert.ok(!both[1].born && !both[1].dies);
});

test("the pairing and its morph are PURE - the same sets give the same path at one m", () => {
  const A = [0, 12].map((x) => boxGroup(x, 8)), B = [boxGroup(4, 14)];
  const once = comparePath(comparePrepare(comparePairGroups(A, B, COMPARE.DEGEN_R)), 0.37);
  const twice = comparePath(comparePrepare(comparePairGroups(A, B, COMPARE.DEGEN_R)), 0.37);
  assert.equal(once, twice, "two calls at one m give the same d, to the digit");
  assert.ok(once.startsWith("M") && once.indexOf("C") > 0, "and it is a path of cubics, not of chords");
  assert.notEqual(once, comparePath(comparePrepare(comparePairGroups(A, B, COMPARE.DEGEN_R)), 0.62), "and m moves it");
});

test("THE BALL'S RADIUS holds the INK'S OWN AREA - never MELT.BALL_R, which is a share of a PAGE's height", () => {
  const area = 900;   /* 900 square page px of ink */
  assert.ok(Math.abs(compareBallR(area, 28) - Math.sqrt(area / Math.PI) * COMPARE.BALL_SWELL) < 1e-9,
            "the ball is the disc that holds the ink");
  assert.equal(compareBallR(0, 28), COMPARE.BALL_MIN * 28, "and never smaller than its floor in figure sizes");
  assert.ok(compareBallR(area, 28) > MELT.BALL_R * 45,
            "a figure's ink box is one line tall: melt's page rule would ball this number up into a speck");
  const c = compareBallC([boxGroup(0, 10), boxGroup(90, 10)]);
  assert.ok(Math.abs(c[0] - 50) < 1e-6, "the centre is the ink's area-weighted centroid: " + c.join(","));
});

test("THE SAG is melt.mjs's own law on the OUTLINES - the top sinks, the foot hangs, the ink never leaves its x", () => {
  const box = { x: 0, y: 0, w: 100, h: 40 }, rnd = compareRnd({ si: 0, idx: 5 }), drips = meltDrips(box, rnd);
  const ring = boxRing(10, 30, 40);
  assert.deepEqual(compareSagAt(ring, 0, box, drips), ring, "at k = 0 the ink stands exactly where the page wrote it");
  const sagged = compareSagAt(ring, 1, box, drips);
  assert.deepEqual(sagged.map((p) => p[0]), ring.map((p) => p[0]), "a melt runs DOWN: no point of the ink moves sideways");
  const foot = Math.max(...sagged.map((p) => p[1])), top = Math.min(...sagged.map((p) => p[1]));
  assert.ok(foot > box.y + box.h, "the foot hangs below the ink box: " + foot);
  assert.ok(top > 0, "and the top has sunk: " + top);
  assert.deepEqual(compareSagAt(ring, 0.5, box, drips), compareSagAt(ring, 0.5, box, drips), "a pure function of k");
});

test("THE SEEDED HASH is the figure's OWN datum - two figures melt differently, one figure melts identically", () => {
  const a = compareRnd({ si: 0, idx: 5 }), b = compareRnd({ si: 1, idx: 5 }), a2 = compareRnd({ si: 0, idx: 5 });
  const read = (r) => [0, 1, 2, 40, 300].map(r);
  assert.deepEqual(read(a), read(a2), "the same datum is the same melt on every frame, seek and render");
  assert.notDeepEqual(read(a), read(b), "another datum is another melt");
  for (const v of read(a)) assert.ok(v >= 0 && v < 1, "a seeded hash is in [0, 1): " + v);
});

test("THE BALL FORM'S FRAME runs melt's OWN phases and lands on the authored strings at both ends", () => {
  const sp = row();
  assert.equal(compareBallFrame(sp, 0, "morph").phase, "melt", "the SAG is melt's first phase");
  assert.equal(compareBallFrame(sp, MELT.MELT_END + 1e-6, "morph").phase, "ball");
  assert.equal(compareBallFrame(sp, MELT.BALL_END + 1e-6, "morph").phase, "fly", "and the ENDING is its third");
  assert.equal(compareBallFrame(sp, 1, "morph").phase, "gone");
  assert.equal(compareBallFrame(sp, 0, "morph").text, "24.8x");
  assert.equal(compareBallFrame(sp, -4, "morph").text, "24.8x");
  assert.equal(compareBallFrame(sp, 1, "morph").text, "15 % dearer");
  assert.equal(compareBallFrame(sp, 9, "morph").text, "15 % dearer");
  assert.equal(compareBallFrame(sp, 1, "morph").morph, 1, "the morph is WHOLE at the end");
  assert.equal(compareBallFrame(sp, 1, "morph").write, 1, "and the figure's own type is what stands there");
  assert.equal(compareBallFrame(sp, 0.99, "morph").write, 0, "the hand never writes the number on a morph: the outlines ARE the glyphs");
  assert.equal(compareBallFrame(sp, 0, "morph").sag, 0);
  assert.equal(compareBallFrame(sp, MELT.MELT_END - 1e-9, "morph").ball, 0, "the ball has not begun while the ink is still sagging");
  assert.equal(compareBallFrame(sp, MELT.BALL_END, "morph").ball, 1, "and is whole exactly when the ending starts");
});

test("THE THREE ENDINGS differ, and each writes the comparator on its OWN clock", () => {
  const sp = row();
  const at = (u, t) => compareBallFrame(sp, u, t);
  assert.equal(at(0.9, "morph").write, 0, "a morph never hands the number to the hand");
  assert.ok(at(0.99, "throw").write > 0, "a throw hands it over once the ball has gone (melt's own release)");
  assert.ok(at(0.99, "splash").write > 0, "a splash hands it over as the splatter dries");
  assert.equal(at(MELT.BALL_END + 1e-6, "throw").write, 0, "neither of them writes while the ball is still on stage");
  assert.equal(at(MELT.BALL_END + 1e-6, "splash").write, 0);
  for (const t of COMPARE_THENS) {
    assert.equal(at(1, t).write, 1, t + ": the comparator is whole at the end");
    assert.equal(at(1, t).text, "15 % dearer", t);
    assert.equal(at(0, t).text, "24.8x", t);
  }
  assert.ok(at(0.7, "splash").burst > 0 && at(0.7, "morph").burst === 0, "only a splash bursts");
  assert.ok(at(0.99, "throw").fly > 0 && at(0.99, "morph").fly === 0, "only a throw flies");
});

test("TWO CALLS AT ONE u GIVE THE SAME ANSWER for the ball form too (a cold seek is the play)", () => {
  for (const then of COMPARE_THENS) {
    for (const u of [0, 0.1, MELT.MELT_END, 0.42, MELT.BALL_END, 0.8, 0.9999, 1]) {
      assert.deepEqual(compareBallFrame(row(), u, then), compareBallFrame(row(), u, then), then + " u=" + u);
    }
  }
  const R = recorder(), ctx = { el: R.el }, sp = row();
  const read = (fg) => ({ chars: fg.__compare.cells.map((c) => c.text), ink: fg.__compare.cells.map((c) => c.at.opacity),
                          ghost: fg.__compare.ghost.at.opacity, d: fg.__compare.ball.ink.at.d,
                          xf: fg.__compare.ball.g.at.transform });
  for (const t of [31.0, 32.2, 32.5, 32.8, 33.1, 33.2, 34.0]) {
    const cold = figureFor("24.8x", R);
    paintCompare({ sp, figures: [cold] }, t, {}, ctx);
    const played = figureFor("24.8x", R);
    for (let k = 0; k <= 30; k++) paintCompare({ sp, figures: [played] }, 31.4 + (t - 31.4) * k / 30, {}, ctx);
    assert.deepEqual(read(cold), read(played), "a cold seek to " + t + " lands where the play does");
  }
});

test("A CALLER WITH NO CANVAS gets the law with NO OUTLINES - never another form, and never an invented face", () => {
  const R = recorder(), ctx = { el: R.el }, sp = row(), fg = figureFor("24.8x", R);
  paintCompare({ sp, figures: [fg] }, 32.0 + 1.2 * 0.4, {}, ctx);   // node: no document, no getComputedStyle
  assert.equal(fg.__compare.ball.ink.at.d, "", "nothing is painted where nothing could be measured");
  assert.equal(fg.__compare.ball.ink.at.opacity, "0.000");
  paintCompare({ sp, figures: [fg] }, 33.2, {}, ctx);
  assert.equal(fg.__compare.cells.map((c) => c.text).join("").replace(/\u00a0/g, " ").trim(), "15 % dearer",
               "and the ends are still the authored strings");
  assert.equal(fg.__compare.ghost.text, "24.8x");
});

test("a degenerate ring is a CIRCLE OF NOTHING at a point - a ring of no length cannot be resampled", () => {
  const seed = compareSeed([12, 34], COMPARE.DEGEN_R);
  assert.ok(seed.length >= 3);
  const c = centroid(seed);
  assert.ok(Math.abs(c[0] - 12) < 1e-6 && Math.abs(c[1] - 34) < 1e-6);
  assert.ok(Math.abs(polyArea(seed)) > 0, "it has an area, so morph_a can walk it by arc length");
});

test("compareGroups reads a GLYPH off the rings: an outer and the holes inside it, in reading order", () => {
  const rings = [{ pts: boxRing(40, 20, 20), hole: false, parent: -1 },
                 { pts: boxRing(0, 20, 20), hole: false, parent: -1 },
                 { pts: boxRing(45, 6, 6), hole: true, parent: 0 }];
  const groups = compareGroups(rings);
  assert.equal(groups.length, 2, "two outers are two glyphs");
  assert.ok(groups[0].c[0] < groups[1].c[0], "sorted by centroid x - the order the hand wrote them in");
  assert.equal(groups[0].holes.length, 0);
  assert.equal(groups[1].holes.length, 1, "and the hole belongs to the glyph it sits in");
});
