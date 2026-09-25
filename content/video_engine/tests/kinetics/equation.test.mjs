// P70 T6 (was P69 T56) - THE EQUATION ROW: the inputs, the relation and the signed result, in spoken order (the Bravos
// harvest v2's T38 and A60, DOM 09:30-09:39). These tests pin the row's order and clock, the hand's write (the figure's
// own figureGlyph), the operators' spring, the layout (one size, the s90 floor, centred, never overlapping), the leave,
// the result's ink, and the painter reached only through ctx - a pure function of t.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { EQUATION, EQUATION_OPS, EQUATION_TERM_MIN, equationItems, equationItemAt, equationOut, equationLayout, equationAdvance,
         paintEquation } from "../../scripts/species/equation.mjs";
import { FIGURE, figureGlyph } from "../../scripts/species/figure.mjs";
import { springPop } from "../../scripts/kinetics/spring.mjs";

const MINUS = "−";
const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const EQ = { kind: "equation", at: 10, dur: 6, target: { kind: "region", x0: 0.06, y0: 0.15, x1: 0.72, y1: 0.29 },
             terms: [{ text: "20%", value: 20, at: 10 }, { text: MINUS + "½", value: -0.5, at: 12.2 }],
             ops: ["×"], result: { text: MINUS + "10%", value: -10, at: 13.44 } };
const BOX = { x: 115.2, y: 162, w: 1267.2, h: 151.2 };   // EQ's region on the 1920 x 1080 stage

test("the dials: the s90 floor, a write shorter than a word gap, an operator's lead inside its word, our hand's ink", () => {
  assert.equal(EQUATION.FLOOR_PX, 59.08, "the s90 floor (ledger_page.CARD_TYPE_PX)");
  assert.ok(EQUATION.OP_LEAD > 0 && EQUATION.OP_LEAD < EQUATION.OP_S && EQUATION.OP_S < EQUATION.WRITE_S);
  assert.ok(EQUATION.OUT_S > 0 && EQUATION.OUT_S < EQUATION.WRITE_S);
  assert.equal(EQUATION.CHAR_W, FIGURE.FIGURE_CHAR_W, "the figure's own advance estimate");
  assert.equal(EQUATION.BASE_DY, FIGURE.BASE_DY, "the figure's own baseline drop");
  const css = readFileSync(new URL("../../../../docs/content-video-engine/samples/scene-evidence-player.template.html", import.meta.url), "utf8");
  assert.equal(EQUATION.NEG, css.match(/--lp-neg: (#[0-9A-Fa-f]{6})/)[1], "E28: the page's neg token, by value");
  assert.equal(EQUATION.CHALK, css.match(/--lp-chalk: (#[0-9A-Fa-f]{6})/)[1], "the page's chalk, by value");
  assert.ok(Object.isFrozen(EQUATION) && Object.isFrozen(EQUATION_OPS));
});

test("the row is laid in SPOKEN order: term, operator, term, =, result - each operator OP_LEAD before the next word", () => {
  const items = equationItems(EQ);
  assert.deepEqual(items.map((i) => i.role), ["term", "op", "term", "eq", "result"]);
  assert.deepEqual(items.map((i) => i.text), ["20%", "×", MINUS + "½", "=", MINUS + "10%"]);
  assert.ok(near(items[1].at, 12.2 - EQUATION.OP_LEAD) && near(items[3].at, 13.44 - EQUATION.OP_LEAD));
  assert.equal(items[4].neg, true, "a negative result is marked for the neg ink");
  const three = equationItems(Object.assign({}, EQ, { terms: [{ text: "2", at: 1 }, { text: "3", at: 2 }, { text: "4", at: 3 }],
                                                      ops: ["x", "-"], result: { text: "-1", value: -1, at: 4 } }));
  assert.deepEqual(three.map((i) => i.text), ["2", "×", "3", MINUS, "4", "=", MINUS + "1"],
                   "ASCII x and - are written as the hand's signs - an operator's, and a number's own minus (review F4)");
});

test("F4: a negative result takes its red from its TEXT's sign - value is optional, a typed hyphen is a minus", () => {
  const res = (r) => equationItems(Object.assign({}, EQ, { result: r })).at(-1);
  assert.equal(res({ text: MINUS + "10%", at: 13.44 }).neg, true, "no value: the written minus is the sign");
  assert.deepEqual([res({ text: "-10%", at: 13.44 }).text, res({ text: "-10%", at: 13.44 }).neg], [MINUS + "10%", true]);
  assert.equal(res({ text: "$" + MINUS + "5B", at: 13.44 }).neg, true, "a minus after the currency");
  assert.equal(res({ text: "10%", value: 10, at: 13.44 }).neg, false);
  assert.equal(res({ text: "+3 pts", at: 13.44 }).neg, false);
  const t = equationItems(Object.assign({}, EQ, { terms: [{ text: "-5%", at: 10 }, EQ.terms[1]] }))[0];
  assert.equal(t.text, MINUS + "5%", "a term's typed hyphen is written as the true minus");
});

test("F7: a term's and the result's label ride their items; F8: the operators are set in the sans, the numbers in the hand", () => {
  const sp = Object.assign({}, EQ, { terms: [Object.assign({}, EQ.terms[0], { label: "AI's weight" }), Object.assign({}, EQ.terms[1], { label: "a halving" })],
                                     result: Object.assign({}, EQ.result, { label: "the index" }) });
  assert.deepEqual(equationItems(sp).map((i) => i.label || null), ["AI's weight", null, "a halving", null, "the index"]);
  assert.equal(EQUATION.LABEL_PX, EQUATION.FLOOR_PX, "the caption at the s90 floor");
  assert.match(EQUATION.OP_FACE, /^Inter/, "x is unmistakable from a letter x in the sans (review F8)");
  assert.notEqual(EQUATION.OP_FACE, EQUATION.FACE);
});

test("F7: the layout keeps room for the labels - under the row, each centred on its item's slot, a slot as wide as its label", () => {
  const adv = [1.6, 0.55, 1.2, 0.55, 2.1], lab = [357, 0, 290, 0, 290];
  const bare = equationLayout(BOX, adv), lay = equationLayout(Object.assign({}, BOX, { h: 200 }), adv, lab);
  assert.ok(lay.fs >= EQUATION_TERM_MIN && !lay.over, "a named row: its numbers at least the step above its captions");
  assert.ok(lay.labelY > lay.y + lay.fs * FIGURE.FIGURE_DOWN, "the captions sit under the row's glyphs");
  lay.slots.forEach((w, i) => assert.ok(w >= lab[i] - 1e-6 && w >= lay.ws[i] - 1e-6, "a slot holds its item and its label"));
  lay.cxs.forEach((cx, i) => assert.ok(near(cx, lay.xs[i] + lay.ws[i] / 2, 1e-6), "the item centred on its slot"));
  assert.ok(lay.w <= BOX.w + 1e-6 && lay.h <= 200 + 1e-6, "it fits the region");
  assert.equal(bare.labelY, null, "no labels, no label line: the unlabelled row lays out as it did");
});

test("round 3: a named row's numbers stand a clear step above their captions - a tight region gives up daylight, never the numbers", () => {
  const capStep = (fs) => (fs * EQUATION.TERM_CAP_K) / (EQUATION.LABEL_PX * EQUATION.LABEL_CAP_K);
  assert.ok(near(capStep(EQUATION_TERM_MIN), EQUATION.STEP) && EQUATION.STEP >= 1.4, "the parent's >= 1.4, measured caps");
  assert.ok(Number(EQUATION.LABEL_WEIGHT) >= 400 && Number(EQUATION.LABEL_WEIGHT) <= 500, "the captions stay quiet");
  const adv = [1.6, 0.55, 1.2, 0.55, 2.1], lab = [300, 0, 250, 0, 240];
  const roomy = equationLayout(Object.assign({}, BOX, { h: 400 }), adv, lab);
  assert.ok(roomy.fs > EQUATION_TERM_MIN && near(roomy.drop, EQUATION.LABEL_DROP) && near(roomy.gap, EQUATION.GAP_K), "room: the numbers grow");
  const low = equationLayout(Object.assign({}, BOX, { h: 170 }), adv, lab);
  assert.ok(near(low.fs, EQUATION_TERM_MIN) && low.drop < EQUATION.LABEL_DROP && low.drop >= EQUATION.DROP_MIN && !low.over,
            "a low region pulls the captions up; the numbers hold the step");
  assert.ok(capStep(low.fs) >= 1.4);
  const narrow = equationLayout(Object.assign({}, BOX, { w: 930, h: 200 }), adv, lab);
  assert.ok(near(narrow.fs, EQUATION_TERM_MIN) && narrow.gap < EQUATION.GAP_K && narrow.gap >= EQUATION.GAP_MIN && !narrow.over,
            "a narrow region closes the gaps; the numbers hold the step");
  const tiny = equationLayout({ x: 100, y: 100, w: 400, h: 80 }, adv, lab);
  assert.ok(tiny.over && near(tiny.fs, EQUATION_TERM_MIN) && near(tiny.gap, EQUATION.GAP_MIN) && near(tiny.drop, EQUATION.DROP_MIN),
            "no region small enough shrinks the numbers: it overflows, and the compiler WARNs");
  const golden = equationLayout({ x: 115.2, y: 140.4, w: 1267.2, h: 179.28 }, adv, [330, 0, 260, 0, 250]);
  assert.ok(!golden.over && capStep(golden.fs) >= 1.4, "the golden's own band holds a named row at the step");
});

test("a term is written by the figure's hand: figureGlyph glyph by glyph over WRITE_S, nothing before its word", () => {
  const term = equationItems(EQ)[0];
  assert.deepEqual(equationItemAt(term, 9.99).glyphs, [0, 0, 0], "before its word: not on the page");
  for (const dt of [0.05, 0.2, 0.35]) {
    const got = equationItemAt(term, 10 + dt).glyphs, u = dt / EQUATION.WRITE_S;
    [0, 1, 2].forEach((j) => assert.ok(near(got[j], figureGlyph(u, j, 3), 1e-12), "the page figure's own law"));
  }
  const whole = 10 + EQUATION.WRITE_S * FIGURE.WRITE * (3 + FIGURE.OVERLAP - 1) / 3;
  assert.deepEqual(equationItemAt(term, whole + 1e-9).glyphs, [1, 1, 1], "the last glyph whole inside the window");
  assert.ok(equationItemAt(term, 10.1).glyphs[2] < equationItemAt(term, 10.1).glyphs[0], "left to right: a hand, not a flash");
});

test("an operator springs on springPop: 0 before its instant, one visible overshoot, exactly 1 once landed", () => {
  const op = equationItems(EQ)[1];
  assert.equal(equationItemAt(op, op.at - 0.01).scale, 0);
  const peak = Math.max(...Array.from({ length: 60 }, (_, i) => equationItemAt(op, op.at + (i / 60) * EQUATION.OP_S).scale));
  assert.ok(peak > 1.0 && near(peak, 1 + EQUATION.POP_MP, 0.01), "the overshoot is the dial's");
  assert.equal(equationItemAt(op, op.at + EQUATION.OP_S + 1e-6).scale, 1, "springPop lands on exactly 1 at its end");
  assert.ok(near(equationItemAt(op, op.at + 0.1).scale, springPop(0.1 / EQUATION.OP_S, EQUATION.POP_MP)));
  const eq = equationItems(EQ)[3];
  assert.ok(eq.at < 13.44 && equationItemAt(eq, 13.44).scale > 0, "= is landing as the result's word begins");
});

test("the row fades over the window's last OUT_S and is gone at its end", () => {
  assert.equal(equationOut(EQ, 12), 1);
  assert.ok(near(equationOut(EQ, 16 - EQUATION.OUT_S / 2), 0.5));
  assert.equal(equationOut(EQ, 16), 0);
});

test("the layout: one size for every item, the region's height shrunk to its width, never under the floor", () => {
  const adv = [1.6, 0.55, 1.2, 0.55, 2.1];
  const lay = equationLayout(BOX, adv);
  assert.ok(near(lay.fs, BOX.h * EQUATION.FS_K), "the height decides when the width has room");
  assert.ok(near(lay.xs[0] - BOX.x, BOX.x + BOX.w - (lay.xs[4] + lay.ws[4]), 1e-6), "centred");
  lay.xs.slice(1).forEach((x, i) => assert.ok(x >= lay.xs[i] + lay.ws[i] + EQUATION.GAP_K * lay.fs - 1e-6, "never overlapping"));
  assert.ok(near(lay.y, BOX.y + BOX.h / 2 + lay.fs * EQUATION.BASE_DY));
  const narrow = equationLayout(Object.assign({}, BOX, { w: 500 }), adv);
  assert.ok(narrow.fs < lay.fs && narrow.fs > EQUATION.FLOOR_PX, "the width decides when the row would not fit");
  assert.ok(near(narrow.w, 500, 1e-6) && !narrow.over, "shrunk to fit the width exactly");
  const tiny = equationLayout({ x: 100, y: 100, w: 200, h: 40 }, adv);
  assert.equal(tiny.fs, EQUATION.FLOOR_PX, "the floor holds even when the region cannot");
  assert.ok(tiny.over && near(tiny.xs[0] - 100, 300 - (tiny.xs[4] + tiny.ws[4]), 1e-6), "and it overflows evenly: the author decides");
});

test("an advance is measured when the glyphs are on the page, CHAR_W per character when nothing can measure", () => {
  assert.ok(near(equationAdvance(null, "20%", 90), 3 * EQUATION.CHAR_W));
  assert.ok(near(equationAdvance({ getComputedTextLength: () => 180 }, "20%", 90), 2));
  assert.ok(near(equationAdvance({ getComputedTextLength: () => 0 }, MINUS + "½", 90), 2 * EQUATION.CHAR_W));
});

// ---------------------------------------------------------------- the painter, through ctx only
const recorder = () => {
  const made = [];
  const el = (tag, cls, parent, at) => {
    const e = { tag, cls, at: Object.assign({}, at || {}), kids: [], textContent: "",
                setAttribute(k, v) { this.at[k] = String(v); },
                getComputedTextLength() { return this.tag === "text" ? this.kids.length * 0.55 * parseFloat(this.at["font-size"]) : 0; } };
    if (parent && parent.kids) parent.kids.push(e);
    made.push(e);
    return e;
  };
  return { el, made, svg: { kids: [] } };
};
const ctxAt = (t, rec, sp = EQ, box = BOX) => ({ sp, t, svg: rec.svg, el: rec.el, resolveTarget: () => box,
                                                 idle: () => ({ scale: 1, dx: 0, dy: 0 }), hash: () => 0.25, seed: 7, si: 0 });
const dump = (n) => JSON.stringify(n, (k, v) => (typeof v === "function" ? undefined : v));

test("the painter writes the whole row in spoken order at its slots, the result in neg, every item at or over the floor", () => {
  const rec = recorder();
  paintEquation(ctxAt(14.2, rec));
  const g = rec.svg.kids[0];
  assert.equal(g.cls, "eqrow");
  const texts = g.kids;
  assert.deepEqual(texts.map((t) => t.at["data-role"]), ["term", "op", "term", "eq", "result"]);
  assert.deepEqual(texts.map((t) => t.kids.map((s) => s.textContent).join("")), ["20%", "×", MINUS + "½", "=", MINUS + "10%"]);
  const xs = texts.map((t) => parseFloat(t.at.x));
  assert.deepEqual(xs, [...xs].sort((a, b) => a - b), "left to right as it is heard");
  assert.ok(texts.every((t) => parseFloat(t.at["font-size"]) >= EQUATION.FLOOR_PX), "the s90 floor");
  assert.equal(texts[4].at.fill, EQUATION.NEG);
  assert.ok(texts.slice(0, 4).every((t) => t.at.fill === EQUATION.CHALK));
  assert.ok(texts[4].kids.every((s) => s.at.opacity === "1.000"), "the result written whole by the golden's instant");
  assert.deepEqual(texts.map((t) => t.at["font-family"]), [EQUATION.FACE, EQUATION.OP_FACE, EQUATION.FACE, EQUATION.OP_FACE, EQUATION.FACE]);
});

test("the painter writes each label under its item at the floor in the page's quiet ink, as its item is written", () => {
  const sp = Object.assign({}, EQ, { terms: [Object.assign({}, EQ.terms[0], { label: "AI's weight" }), EQ.terms[1]],
                                     result: Object.assign({}, EQ.result, { label: "the index" }) });
  const at = (t) => { const rec = recorder(); paintEquation(ctxAt(t, rec, sp)); return rec.svg.kids[0].kids; };
  const all = at(14.2), labs = all.filter((n) => n.at["data-role"] === "label"), items = all.filter((n) => n.at["data-role"] !== "label");
  assert.deepEqual(labs.map((l) => l.textContent), ["AI's weight", "the index"]);
  assert.ok(labs.every((l) => l.at.fill === EQUATION.LABEL_INK && parseFloat(l.at["font-size"]) === EQUATION.LABEL_PX
                              && l.at["text-anchor"] === "middle" && l.at["font-family"] === EQUATION.LABEL_FACE));
  assert.ok(labs.every((l) => parseFloat(l.at.y) > parseFloat(items[0].at.y)), "under the row");
  const x0 = parseFloat(items[0].at.x), w0 = items[0].kids.length * 0.55 * parseFloat(items[0].at["font-size"]);
  assert.ok(near(parseFloat(labs[0].at.x), x0 + w0 / 2, 0.11), "centred under its own term");
  const early = at(10.1).filter((n) => n.at["data-role"] === "label");
  assert.ok(parseFloat(early[0].at.opacity) > 0 && parseFloat(early[0].at.opacity) < 1, "the first caption arrives with its term");
  assert.equal(early[1].at.opacity, "0.000", "the result's caption waits for the result's word");
});

test("the painter is a pure function of t, holds every slot from the first frame, and draws nothing unresolved or gone", () => {
  const a = recorder(), b = recorder();
  paintEquation(ctxAt(12.3, a)); paintEquation(ctxAt(12.3, b));
  assert.equal(dump(a.svg), dump(b.svg), "the same t, the same row");
  const early = recorder(), late = recorder();
  paintEquation(ctxAt(10.2, early)); paintEquation(ctxAt(14.2, late));
  assert.deepEqual(early.svg.kids[0].kids.map((t) => t.at.x), late.svg.kids[0].kids.map((t) => t.at.x),
                   "a later term never moves an earlier one: every slot stands from the first frame");
  assert.ok(early.svg.kids[0].kids[4].kids.every((s) => s.at.opacity === "0.000"), "the result waits for its word");
  const none = recorder();
  paintEquation(Object.assign(ctxAt(12, none), { resolveTarget: () => null }));
  assert.equal(none.svg.kids.length, 0, "the targeting law");
  const gone = recorder();
  paintEquation(ctxAt(16, gone));
  assert.equal(gone.svg.kids.length, 0, "the row has left");
});
