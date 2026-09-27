// P57 T20 / R26-98 - THE FIGURE PROMOTED (the P55 T7 recipe), a PAGE painter. The promotion's proof is that
// every golden is byte-identical, so what this file pins is that the module still carries the INLINE ENGINE's
// numbers and arithmetic: R26-71's step-off (the box, the quanta, the side `dy` chose, the caps), the authored
// place both the BUILDER and the PAINTER now read through one function, and the hand's write clock - the figure
// over the first 0.6 of the word, the sub over the rest, each glyph with the 1.6 overlap. The painter is called
// on recorders with no DOM: it reaches the engine only through its page ctx (markDatum, pointsNow, PS).
import { test } from "node:test";
import assert from "node:assert/strict";
import * as FIG_MOD from "../../scripts/species/figure.mjs";
import { FIGURE, segMeetsBox, boxMeetsBox, figBox, figWidth, figClearY, figurePlace, figureGlyph, figureSubGlyph,
         figureHandOver, figureHandBack, paintFigure } from "../../scripts/species/figure.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const clamp01 = (v) => Math.min(1, Math.max(0, v));   // the engine's own, verbatim
const PS = { BRACKET_GAP: 34, BRACKET_ROOM: 200 };    // the bracket's dials, as PAGE_CTX hands them over

/* a recorder in an SVG element's shape: every attribute the painter writes, kept */
const node = () => { const a = {}; return { a, setAttribute: (k, v) => { a[k] = v; } }; };
/* the perform layer's BUILT figure, as buildPerform returns it (the record species/compare.mjs reads) */
const built = (o = {}) => Object.assign({
  sp: { kind: "figure", at: 10, dur: 2, text: "1,074 index", sub: "the peak", dy: -0.9 },
  D: [800, 300], x: 814, y: 260, fits: true, g: node(), label: node(), sub: node(),
  lg: [node(), node(), node(), node()], sg: [node(), node()],
  fi: 0, fs: 26, fss: 20, W: 1000, H: 560, tw: 140, subH: 26, si: 0, idx: 191,
}, o);

// ---------------------------------------------------------------- the dials, as the inline code carried them
test("every dial is the inline engine's literal, to the digit, and frozen", () => {
  assert.ok(Object.isFrozen(FIGURE));
  assert.equal(FIGURE.FIGURE_STEP, 0.6, "PS.FIGURE_STEP - one quantum off the ink");
  assert.equal(FIGURE.FIGURE_STEPS, 4, "PS.FIGURE_STEPS - the cap either side");
  assert.equal(FIGURE.FIGURE_PAD, 5, "PS.FIGURE_PAD - the daylight kept from the stroke");
  assert.equal(FIGURE.FIGURE_UP, 1.08, "PS.FIGURE_UP - the glyph box above the baseline");
  assert.equal(FIGURE.FIGURE_DOWN, 0.53, "PS.FIGURE_DOWN - and below it");
  assert.equal(FIGURE.FIGURE_CHAR_W, 0.62, "PS.FIGURE_CHAR_W - the advance when nothing can measure");
  assert.equal(FIGURE.X_PAD, 14, "D[0] + 14 / D[0] - 14");
  assert.equal(FIGURE.BASE_DY, 0.35, "D[1] + fs * 0.35");
  assert.equal(FIGURE.LINE, 1.2, "(Number(sp.dy) || 0) * fs * 1.2");
  assert.equal(FIGURE.SUB_DY, 1.3, "the sub's baseline: y + fss * 1.3");
  assert.deepEqual([FIGURE.WRITE, FIGURE.SUB_WRITE], [0.6, 0.4], "perL = 0.6 / nl, perS = 0.4 / ns");
  assert.equal(FIGURE.OVERLAP, 1.6, "(uL - j * perL) / (perL * 1.6)");
  assert.ok(near(FIGURE.WRITE + FIGURE.SUB_WRITE, 1), "the figure and its sub are the whole word");
});

// ---------------------------------------------------------------- the authored place (E50)
test("the number is written beside its datum, on the side the chart has room on", () => {
  const q = figurePlace([700, 300], 26, 0, 1000, PS.BRACKET_GAP, PS.BRACKET_ROOM);
  assert.equal(q.fits, true, "700 + 34 + 200 <= 1000 - the bracket's own room test");
  assert.equal(q.x, 714, "the authored place is the datum plus X_PAD");
  assert.equal(q.anchor, "start", "written rightward, away from the line's own history");
  assert.ok(near(q.yA, 300 + 26 * 0.35), "the baseline sits on the point, dropped BASE_DY");
  assert.equal(figurePlace([800, 300], 26, 0, 1000, PS.BRACKET_GAP, PS.BRACKET_ROOM).fits, false,
               "800 + 34 + 200 > 1000: the room runs out before the page's edge does");
});

test("a datum with no room to its right writes LEFTWARD, anchored end (the peak at the page's edge)", () => {
  const q = figurePlace([800, 300], 26, 0, 1000, PS.BRACKET_GAP, PS.BRACKET_ROOM + 1);
  assert.equal(q.fits, false, "one unit of room short is no room");
  assert.equal(q.x, 786, "D[0] - X_PAD");
  assert.equal(q.anchor, "end", "the golden `page-figure`'s own branch");
});

test("the authored `dy` moves the baseline by LINEs of the figure's own size, negative UP", () => {
  const up = figurePlace([800, 300], 40, -0.9, 1000, PS.BRACKET_GAP, PS.BRACKET_ROOM);
  const down = figurePlace([800, 300], 40, 0.9, 1000, PS.BRACKET_GAP, PS.BRACKET_ROOM);
  assert.ok(near(up.yA, 300 + 40 * 0.35 + -0.9 * 40 * 1.2), "the inline engine's own expression");
  assert.ok(up.yA < down.yA, "negative is up the page");
  assert.ok(near(figurePlace([800, 300], 40, undefined, 1000, 34, 200).yA, 300 + 40 * 0.35),
            "an unauthored dy is no dy - Number(undefined) || 0");
});

// ---------------------------------------------------------------- R26-71: the box and the ink
test("the box is the advance and the glyph box either side of the baseline, the sub hanging under it", () => {
  assert.deepEqual(figBox(100, 200, 140, 26, "start", 0),
                   [100, 200 - 1.08 * 26, 140, (1.08 + 0.53) * 26]);
  assert.deepEqual(figBox(100, 200, 140, 26, "end", 26),
                   [100 - 140, 200 - 1.08 * 26, 140, (1.08 + 0.53) * 26 + 26], "an `end` box reaches back");
});

test("the advance is MEASURED where the glyphs are, and arithmetic where nothing can measure", () => {
  assert.equal(figWidth({ getComputedTextLength: () => 137.5 }, "1,074 index", 26), 137.5, "the written width");
  assert.equal(figWidth(null, "abcde", 40), 5 * 40 * 0.62, "FIGURE_CHAR_W per character");
  assert.equal(figWidth({ getComputedTextLength: () => 0 }, "abcde", 40), 5 * 40 * 0.62,
               "a measure of zero is no measure (the font has not loaded)");
});

test("Liang-Barsky: a segment through the box meets it, one far off does not, and the pad is ink", () => {
  const box = [100, 100, 200, 60];
  assert.equal(segMeetsBox([90, 130], [310, 130], box, 0), true, "straight through");
  assert.equal(segMeetsBox([90, 400], [310, 400], box, 0), false, "far below");
  assert.equal(segMeetsBox([90, 95], [310, 95], box, 8), true, "inside the pad counts as ink");
  assert.equal(segMeetsBox([90, 95], [310, 95], box, 0), false, "... and outside it does not");
});

// a line that stands flat and then CLIMBS - the bridge short's own shape, the one `31% of GDP` was printed across
const CLIMB = Array.from({ length: 40 }, (_, i) => [100 + i * 20, i < 20 ? 400 : 400 - (i - 20) * 14]);
const FLAT = Array.from({ length: 40 }, (_, i) => [100 + i * 20, 500]);

test("a figure with nothing in its way does not move by a thousandth (the clear case)", () => {
  assert.equal(figClearY(200, 300, 140, 26, "start", -0.9, FLAT, 0, 560), 300,
               "the authored place is only ever left for INK");
});

test("a figure over its own line steps off it, in whole quanta of FIGURE_STEP * fs", () => {
  const yA = 400, fs = 26;   // the flat run of CLIMB is at y 400: the authored box sits ON the stroke
  const y = figClearY(300, yA, 140, fs, "start", -0.9, CLIMB, 0, 560);
  assert.notEqual(y, yA, "the box met the stroke: R26-71 says it moves");
  const k = (y - yA) / (FIGURE.FIGURE_STEP * fs);
  assert.ok(near(k, Math.round(k)), `moved ${y - yA}, not a whole quantum`);
  assert.ok(Math.abs(Math.round(k)) >= 1 && Math.abs(Math.round(k)) <= FIGURE.FIGURE_STEPS, "within the cap");
  assert.ok(k < 0, "the side the authored `dy` already chose goes FIRST: dy was up");
});

test("the side is the authored `dy`'s, first - a positive dy steps DOWN before it tries up", () => {
  const yA = 400, fs = 26;
  const down = figClearY(300, yA, 140, fs, "start", 0.9, CLIMB, 0, 560);
  assert.ok(down > yA, "dy pushed it below the datum: it keeps pushing");
});

test("the step is capped at the chart's own box, and nowhere clear leaves the authored place", () => {
  const yA = 20, fs = 26;   // hard against the top of a 40-unit page: every step up leaves the box
  const y = figClearY(300, yA, 140, fs, "start", -0.9, CLIMB, 0, 40);
  assert.equal(y, yA, "nowhere clear = the authored place, and the collision gate still says so");
  assert.equal(figClearY(300, 380, 140, 26, "start", -0.9, [[0, 0]], 0, 560), 380, "one point is not a stroke");
  assert.equal(figClearY(300, 380, 0, 26, "start", -0.9, CLIMB, 0, 560), 380, "an unmeasured width is no box");
});

// ------------------------------------------------- R26-191: the step-off never lands on the page's own labels
// TOKYO, THE TWO FRAMES. The approved 2026-09-11 cut and a 2026-09-15 rebuild of the same beat differ in ONE
// box: the figure "$1,116.7B" on the customs page at t=25.56, [594, 1032, 145, 64] approved and [594, 1128,
// 146, 64] rebuilt - 96 px lower, 4 x FIGURE_STEP x 40, the whole ladder - where the month tick "Jun '26"
// stands at [690, 1161, 128, 44] and the series name at [374, 1089, 254, 49]. The step-off had walked off its
// own ink onto the axis. The numbers below are those boxes; the ink is a stroke that blocks every candidate but
// the last, which is the case that broke.
const TOKYO = {
  x: 594, fs: 40, tw: 145, anchor: "start", dy: -0.9, H: 1920,
  yA: 1032 + FIGURE.FIGURE_UP * 40,        // the approved cut's box TOP is the baseline less the glyph box
  tick: [690, 1161, 128, 44],              // tick:Jun '26, as probe.py measured it on both builds
  ink: [[600, 980], [700, 1120]],          // the series' stroke across every candidate place but the fourth down
};
const tokyoY = (avoid) => figClearY(TOKYO.x, TOKYO.yA, TOKYO.tw, TOKYO.fs, TOKYO.anchor, TOKYO.dy,
                                    TOKYO.ink, 0, TOKYO.H, avoid);

test("two boxes MEET when they overlap on both axes, with the stroke's own daylight between them", () => {
  assert.equal(boxMeetsBox([0, 0, 10, 10], [20, 0, 10, 10], 0), false, "clear on x");
  assert.equal(boxMeetsBox([0, 0, 10, 10], [0, 20, 10, 10], 0), false, "clear on y");
  assert.equal(boxMeetsBox([0, 0, 10, 10], [9, 9, 10, 10], 0), true, "a corner is a meeting");
  assert.equal(boxMeetsBox([0, 0, 10, 10], [12, 0, 10, 10], 0), false, "2 px of air, no pad: clear");
  assert.equal(boxMeetsBox([0, 0, 10, 10], [12, 0, 10, 10], FIGURE.FIGURE_PAD), true,
               "the same 2 px inside the pad: the eye reads them as one");
});

test("R26-191: the step off the ink refuses a place that lands on one of the page's own labels", () => {
  const regression = tokyoY(null);   // the 09-14 step-off: ink and the chart's box, nothing else
  assert.ok(near(regression - TOKYO.yA, 4 * FIGURE.FIGURE_STEP * TOKYO.fs),
            `the ladder's last rung is the only one clear of ink (moved ${regression - TOKYO.yA})`);
  assert.equal(boxMeetsBox(figBox(TOKYO.x, regression, TOKYO.tw, TOKYO.fs, TOKYO.anchor, 0), TOKYO.tick,
                           FIGURE.FIGURE_PAD), true, "... and it is ON the month tick - the rebuilt frame");
  const y = tokyoY([TOKYO.tick]);
  assert.equal(boxMeetsBox(figBox(TOKYO.x, y, TOKYO.tw, TOKYO.fs, TOKYO.anchor, 0), TOKYO.tick,
                           FIGURE.FIGURE_PAD), false, "the restored step-off keeps off the label");
  assert.equal(y, TOKYO.yA, "nowhere clear of BOTH = the authored place, which is the approved 09-11 frame");
  assert.equal(figBox(TOKYO.x, y, TOKYO.tw, TOKYO.fs, TOKYO.anchor, 0)[1], 1032,
               "the box top the approved cut measured, to the pixel");
});

test("R26-191: a label never PUSHES a figure - only ink moves one, exactly as before", () => {
  const onTheLabel = [figBox(200, 300, 140, 26, "start", 0)];   // a label squarely at the authored place
  assert.equal(figClearY(200, 300, 140, 26, "start", -0.9, FLAT, 0, 560, onTheLabel), 300,
               "the authored place is still only ever left for INK (R26-71's trigger, unchanged)");
  assert.equal(figClearY(200, 300, 140, 26, "start", -0.9, FLAT, 0, 560, []), 300, "an empty list is no list");
  assert.equal(figClearY(200, 300, 140, 26, "start", -0.9, FLAT, 0, 560, [[1, 2, 3]]), 300,
               "a malformed box is ignored, never thrown on");
});

test("R26-191: a figure with a clear rung TAKES it - the step-off still steps", () => {
  const y = figClearY(300, 400, 140, 26, "start", -0.9, CLIMB, 0, 560, [[0, 0, 1, 1]]);
  assert.notEqual(y, 400, "a label nowhere near the ladder changes nothing");
  assert.equal(y, figClearY(300, 400, 140, 26, "start", -0.9, CLIMB, 0, 560), "the same rung as before R26-191");
});

// ---------------------------------------------------------------- the hand's clock
test("the figure writes over the first 0.6 of the word, glyph by glyph, with the hand's overlap", () => {
  assert.equal(figureGlyph(0, 0, 4), 0, "nothing before the word");
  assert.ok(near(figureGlyph(0.15, 0, 4), clamp01((0.15 - 0) / ((0.6 / 4) * 1.6))), "the inline expression");
  assert.ok(figureGlyph(0.3, 0, 4) > figureGlyph(0.3, 3, 4), "the hand runs left to right");
  /* THE TAIL, as the inline engine writes it and this module keeps it: the last glyph is still arriving when
     the figure's own share ends - at WRITE it stands at 0.625 - and it is fully in at j * per + per * OVERLAP
     (0.69 of the word), inside the sub's share. The hand overruns its own beat; it does not clip. */
  assert.ok(near(figureGlyph(0.6, 3, 4), 0.625), "the last glyph at WRITE - the inline engine's own tail");
  assert.equal(figureGlyph(0.69, 3, 4), 1, "... fully in a hair later, inside the sub's share");
  for (let j = 0; j < 4; j++) assert.equal(figureGlyph(1, j, 4), 1, "the whole number stands at the word's end");
});

test("the sub writes over the remaining 0.4, starting where the figure's own write ended", () => {
  assert.equal(figureSubGlyph(0.6, 0, 2), 0, "not a glyph of it before WRITE");
  assert.ok(figureSubGlyph(0.8, 0, 2) > 0, "... and it is running after");
  assert.ok(near(figureSubGlyph(0.9, 1, 2),
                 clamp01((0.9 - 0.6 - 1 * (0.4 / 2.6)) / ((0.4 / 2.6) * 1.6))), "the share is 0.4 / (n + 0.6)");
  /* R26-314 (P71 T1): the SUB has no room after it to finish in - `u` is clamped at 1 - so at the promotion's
     share of 0.4 / n its last glyph held at 0.625 from the end of the word on, which is what the inline engine
     had always painted (H row 10 read "averag" plus a dim "e"). The share is now 0.4 / (n + OVERLAP - 1), the
     span's and the comparator's law, and the last glyph is whole exactly as the word ends - the assertion that
     recorded the tail at 0.625 is inverted here, not deleted. */
  assert.equal(figureSubGlyph(1, 1, 2), 1, "the sub's last glyph is whole at the word's end");
  assert.equal(figureSubGlyph(1, 0, 2), 1, "every glyph before it is fully in");
});

/* R26-314 (P71 T1): H row 10's "$28B a year" figure read "averag" plus a dim "e" from its word's end on. The law
   the span (spanGlyph) and the comparator (compareGlyph) already carry: the share is SUB_WRITE / (n + OVERLAP - 1),
   so the LAST glyph is fully in exactly when the word ends - never before, and never held part-written after. */
const oldSubGlyph = (u, j, n) => clamp01((u - 0.6 - j * (0.4 / Math.max(1, n))) / ((0.4 / Math.max(1, n)) * 1.6));
const oldFigGlyph = (u, j, n) => clamp01((u - j * (0.6 / Math.max(1, n))) / ((0.6 / Math.max(1, n)) * 1.6));
const lcg = (seed) => () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);

test("R26-314: the sub writes its last letter exactly when its word ends, for every length", () => {
  for (let n = 1; n <= 40; n++) {
    assert.equal(figureSubGlyph(1, n - 1, n), 1, `n=${n}: the last glyph is whole at the word's end`);
    assert.ok(figureSubGlyph(0.99, n - 1, n) < 1, `n=${n}: ... and not before it - the hand still runs to the end`);
  }
});

test("R26-314: every sub glyph is monotone in u and never less written than before the fix", () => {
  for (let n = 1; n <= 40; n++) for (let j = 0; j < n; j++) {
    let prev = -1;
    for (let k = 0; k <= 400; k++) {
      const u = k / 400, v = figureSubGlyph(u, j, n);
      assert.ok(v >= prev, `n=${n} j=${j} u=${u}: monotone`);
      assert.ok(v >= oldSubGlyph(u, j, n), `n=${n} j=${j} u=${u}: at or above the 1 / n share`);
      prev = v;
    }
  }
});

test("R26-314: the figure's own line (figureGlyph) is untouched - byte-identical over 1000 samples", () => {
  const r = lcg(314);
  for (let i = 0; i < 1000; i++) {
    const n = 1 + Math.floor(r() * 40), j = Math.floor(r() * n), u = r() * 1.2 - 0.1;
    assert.equal(figureGlyph(u, j, n), oldFigGlyph(u, j, n), `u=${u} j=${j} n=${n}`);
  }
});

// ---------------------------------------------------------------- the painter, on recorders, with no DOM
test("the painter writes the glyph opacities to three places, and nothing before the word", () => {
  const fg = built();
  paintFigure(fg, 9, null, { PS });
  assert.equal(fg.g.a.opacity, 0, "t < at: nothing on the page");
  paintFigure(fg, 12, null, { PS });
  assert.equal(fg.g.a.opacity, 1);
  assert.deepEqual(fg.lg.map((n) => n.a.opacity), ["1.000", "1.000", "1.000", "1.000"]);
  assert.deepEqual(fg.sg.map((n) => n.a.opacity), ["1.000", "1.000"], "the sub is whole at the word's end (R26-314)");
  const mid = built();
  paintFigure(mid, 10.3, null, { PS });
  assert.equal(mid.lg[0].a.opacity, figureGlyph(0.15, 0, 4).toFixed(3), "the same number, written the same way");
  assert.equal(mid.sg[0].a.opacity, "0.000", "the sub has not started");
});

test("a page with STATES re-reads the datum, and a dropped one shows nothing (P48 T7 / R26-28)", () => {
  const st = { states: [{}, {}], active: 1 };
  const ctx = { PS, markDatum: () => null, pointsNow: () => [] };
  const gone = built();
  paintFigure(gone, 12, st, ctx);
  assert.equal(gone.g.a.opacity, 0, "a datum the window dropped is not drawn somewhere else");

  const live = built();
  const pts = FLAT.map((p, i) => ({ i, p }));
  paintFigure(live, 12, st, { PS, markDatum: () => [400, 300], pointsNow: () => pts });
  const q = figurePlace([400, 300], live.fs, live.sp.dy, live.W, PS.BRACKET_GAP, PS.BRACKET_ROOM);
  assert.equal(live.label.a.x, q.x.toFixed(1), "it follows the ACTIVE state's datum");
  assert.equal(live.label.a["text-anchor"], q.anchor);
  assert.equal(live.label.a.y, live.y.toFixed(1), "the attribute is the record, to one decimal");
  assert.equal(live.sub.a.y, (live.y + live.fss * FIGURE.SUB_DY).toFixed(1), "the sub hangs under it");
  assert.deepEqual([live.x, live.fits], [q.x, q.fits],
                   "the record species/compare.mjs reads (PF.figures) is written back");
  assert.deepEqual(live.D, [400, 300]);
});

test("the same instant, painted twice, lands on the same attributes (a seek is a play)", () => {
  const st = { states: [{}, {}], active: 1 };
  const ctx = { PS, markDatum: () => [400, 380], pointsNow: () => CLIMB.map((p, i) => ({ i, p })) };
  const a = built(), b = built();
  paintFigure(a, 11.4, st, ctx);
  for (const t of [10.2, 10.8, 11.0, 11.4]) paintFigure(b, t, st, ctx);
  assert.deepEqual(b.label.a, a.label.a, "nothing here integrates: the frame is a function of t");
  assert.deepEqual(b.lg.map((n) => n.a.opacity), a.lg.map((n) => n.a.opacity));
});

// ---------------------------------------------------------------- P72 T18: the hand-over in place (R26-284) and the bar's anchor (R26-255)
test("R26-284: the hand-over's two dials, and the base write untouched when nothing stood", () => {
  assert.equal(FIGURE.HAND, 0.4, "the share of the word the standing number takes to leave");
  assert.equal(FIGURE.BACK, 0.5, "the share of the leave the figure takes before the number returns");
  assert.ok(FIGURE.HAND > 0.3, "test_compare_on_bars reads the value mid-leave at u = 0.3");
  for (const u of [0, 0.1, 0.3, 0.59, 0.6, 1]) {
    const h = figureHandOver(u, false);
    assert.equal(h.show, 1, "a number that had not stood: the figure is up from its word");
    assert.equal(h.uf, u, "... and writes on its own clock, to the bit");
    assert.equal(h.number, 1 - clamp01(u / FIGURE.WRITE), "... and the value yields as it always did (u / WRITE)");
  }
});

test("R26-284: a number that STOOD leaves first, and the hand writes after it - never both up", () => {
  let last = -1;
  for (let k = 0; k <= 1000; k++) {
    const u = k / 1000, h = figureHandOver(u, true);
    assert.ok(!(h.number > 0 && h.show > 0), `u=${u}: the number (${h.number}) and the figure are both up`);
    assert.ok(h.uf >= last, "the hand never writes backwards"); last = h.uf;
    if (u < FIGURE.HAND) assert.equal(h.uf, 0, "no glyph before the number has gone");
  }
  assert.equal(figureHandOver(0, true).number, 1, "at the word the number still stands");
  assert.equal(figureHandOver(FIGURE.HAND, true).number, 0);
  assert.equal(figureHandOver(1, true).uf, 1, "and the figure is whole at the word's end");
});

test("R26-284: on the leave the figure goes first and the number returns after it", () => {
  for (let k = 0; k <= 100; k++) {
    const lv = k / 100, b = figureHandBack(lv);
    assert.ok(!(b.figure > 0 && b.number > 0), `lv=${lv}: both up`);
  }
  assert.deepEqual(figureHandBack(0), { figure: 1, number: 0 });
  assert.deepEqual(figureHandBack(1), { figure: 0, number: 1 });
});

test("R26-284: the painter holds a figure whose number stood, then writes it on the remaining word", () => {
  const fg = built({ stood: true });
  paintFigure(fg, 10 + 2 * 0.2, null, { PS });
  assert.equal(fg.g.a.opacity, 0, "u = 0.2: the number is still leaving - the figure is not up");
  paintFigure(fg, 10 + 2 * 0.7, null, { PS });
  const uf = (0.7 - FIGURE.HAND) / (1 - FIGURE.HAND);
  assert.equal(fg.g.a.opacity, 1);
  assert.equal(fg.lg[0].a.opacity, figureGlyph(uf, 0, 4).toFixed(3), "the hand's own law, on the remaining word");
  const plain = built();
  paintFigure(plain, 10 + 2 * 0.2, null, { PS });
  assert.equal(plain.g.a.opacity, 1, "a figure with no standing number is untouched");
  assert.equal(plain.lg[0].a.opacity, figureGlyph(0.2, 0, 4).toFixed(3));
});

test("R26-255: on a page with STATES a centred bar figure keeps its anchor and rides its bar's top", () => {
  const st = { states: [{}, {}], active: 1 };
  const bar = built({ anchor: "middle", bar: {}, D: [500, 300], x: 500, y: 280, fits: true });
  paintFigure(bar, 12, st, { PS, markDatum: () => [540, 260], pointsNow: () => [] });
  assert.equal(bar.label.a["text-anchor"], "middle", "never re-placed beside its bar by the line rule");
  assert.equal(bar.label.a.x, (540).toFixed(1), "centred on the bar's top as the active state draws it");
  assert.equal(bar.label.a.y, (240).toFixed(1), "at the same offset from that top the builder chose");
  assert.equal(bar.sub.a.y, (240 + bar.fss * FIGURE.SUB_DY).toFixed(1));
  assert.deepEqual([bar.x, bar.y, bar.fits, bar.anchor], [540, 240, true, "middle"], "the record compare.mjs reads");
  const again = built({ anchor: "middle", bar: {}, D: [500, 300], x: 500, y: 280, fits: true });
  for (const t of [11, 12.5, 12]) paintFigure(again, t, st, { PS, markDatum: () => [540, 260], pointsNow: () => [] });
  assert.deepEqual(again.label.a, bar.label.a, "a seek is a play: the offset is the BUILT one, never re-accumulated");
  const lerp = built({ anchor: "middle", bar: {}, D: [500, 300], x: 500, y: 280 });
  paintFigure(lerp, 12, st, { PS, markDatum: () => [540, 260], datumNow: () => [520, 280], pointsNow: () => [] });
  assert.equal(lerp.label.a.x, (520).toFixed(1), "across a rescale it rides the bar as it MOVES (datumNow, the lerped datum)");
  const line = built();
  paintFigure(line, 12, st, { PS, markDatum: () => [400, 300], datumNow: () => [10, 10], pointsNow: () => FLAT.map((p, i) => ({ i, p })) });
  assert.equal(line.label.a.x, figurePlace([400, 300], line.fs, line.sp.dy, line.W, PS.BRACKET_GAP, PS.BRACKET_ROOM).x.toFixed(1),
               "a LINE figure still reads the active state's datum, as before");
  const gone = built({ anchor: "middle", bar: {}, D: [500, 300], x: 500, y: 280 });
  paintFigure(gone, 12, st, { PS, markDatum: () => null, pointsNow: () => [] });
  assert.equal(gone.g.a.opacity, 0, "a bar the state dropped shows nothing");
});

// ---------------------------------------------------------------- P72 T46g (R26-409): a figure on a MOVING datum
// H row 16's "$121B" held its old place for the whole of the extend's rescale (12.2-13.0 s) while its datum travelled
// 180 px left and 90 px down, then JUMPED - and changed side (written leftward at the page's edge, rightward after). A
// figure now tweens from its place on the leaving state to its place on the arriving one, on the datum's own eased clock
// (the engine's `xfClock`, the one lpDatumNow lerps on), so it rides its datum and never jumps - its side included.
const { figureTween, figureLinePlace } = FIG_MOD;
const S_A = { name: "leaving" }, S_B = { name: "arriving" };
const D_A = [900, 100], D_B = [500, 300];   /* at the page's right edge (no room: leftward), then with room (rightward) */
const moving = (u, o = {}) => {
  const st = { states: [S_A, S_B], active: o.active ?? 0, labBoxes: [] };
  const on = (v) => v.states[v.active | 0];
  const ctx = { PS,
    markDatum: (v, si, i) => { assert.equal(i, 191); const S = on(v);
      if (o.dropOn === S) return null; return S === S_A ? D_A : D_B; },
    pointsNow: () => [],
    datumNow: () => { throw new Error("the line figure reads the two states' places, not the lerped datum alone"); },
    xfClock: (v) => (v === st && u !== null ? { from: 0, to: 1, u } : null) };
  return { st, ctx };
};
const placeOn = (fg, D) => figureLinePlace(fg, D, [], [], PS);
const leftOf = (p, tw) => (p.anchor === "end" ? p.x - tw : p.x);

test("R26-409: the place on ONE state is the builder's law - figurePlace, then R26-71's step-off", () => {
  const fg = built();
  const p = placeOn(fg, D_A), q = figurePlace(D_A, fg.fs, fg.sp.dy, fg.W, PS.BRACKET_GAP, PS.BRACKET_ROOM);
  assert.deepEqual(p, { x: q.x, y: q.yA, anchor: q.anchor, fits: q.fits });
  assert.equal(p.anchor, "end", "the datum at the page's edge writes leftward");
  assert.equal(placeOn(fg, D_B).anchor, "start");
});

test("R26-409: the tween is EXACTLY each state's place at its two ends, and the left edge lerps between", () => {
  const fg = built(), pa = placeOn(fg, D_A), pb = placeOn(fg, D_B);
  assert.deepEqual(figureTween(pa, pb, 0, fg.tw), pa, "u = 0 is the leaving state's place, anchor and all");
  assert.deepEqual(figureTween(pa, pb, 1, fg.tw), pb, "u = 1 is the arriving state's");
  const m = figureTween(pa, pb, 0.5, fg.tw);
  assert.equal(m.anchor, "start", "across a change of side the text is placed by its LEFT edge ...");
  assert.ok(near(m.x, (leftOf(pa, fg.tw) + leftOf(pb, fg.tw)) / 2), "... which lerps");
  assert.ok(near(m.y, (pa.y + pb.y) / 2));
  const same = figureTween(pb, Object.assign({}, pb, { x: pb.x + 100, y: pb.y - 50 }), 0.25, fg.tw);
  assert.equal(same.anchor, "start"); assert.ok(near(same.x, pb.x + 25) && near(same.y, pb.y - 12.5));
});

test("R26-409: the painter RIDES the datum through the re-fit - no frame jumps, its side change included", () => {
  let prev = null, worst = 0;
  for (let k = 0; k <= 100; k++) {
    const u = k / 100, fg = built(), { st, ctx } = moving(u, { active: u >= 0.5 ? 1 : 0 });
    paintFigure(fg, 12, st, ctx);
    const x = +fg.label.a.x, y = +fg.label.a.y, L = fg.label.a["text-anchor"] === "end" ? x - fg.tw : x;
    if (prev) worst = Math.max(worst, Math.hypot(L - prev[0], y - prev[1]));
    prev = [L, y];
    assert.equal(fg.g.a.opacity, 1);
  }
  const span = Math.hypot(leftOf(placeOn(built(), D_B), 140) - leftOf(placeOn(built(), D_A), 140), 200);
  assert.ok(worst <= span / 100 + 0.2, `the biggest step between two hundredths of the move: ${worst} px of ${span}`);
});

test("R26-409: the record compare.mjs reads is the datum THIS frame, and the ends are the states' own", () => {
  const fg = built(), { st, ctx } = moving(0.25);
  paintFigure(fg, 12, st, ctx);
  assert.deepEqual(fg.D, [800, 150], "the lerped datum - lpDatumNow's own arithmetic");
  const a = built(), A = moving(0);
  paintFigure(a, 12, A.st, A.ctx);
  const pa = placeOn(built(), D_A);
  assert.deepEqual([a.label.a.x, a.label.a.y, a.label.a["text-anchor"]], [pa.x.toFixed(1), pa.y.toFixed(1), pa.anchor],
                   "u = 0: the frame the base painted, to the attribute");
});

test("R26-409: no re-fit, or a datum one side lacks - the ACTIVE state's datum, as before", () => {
  for (const [u, o] of [[null, {}], [0.5, { dropOn: S_B }], [0.5, { dropOn: S_A, active: 1 }]]) {
    const fg = built(), { st, ctx } = moving(u, o);
    paintFigure(fg, 12, st, ctx);
    const D = o.active === 1 ? D_B : D_A, q = placeOn(built(), D);
    assert.equal(fg.label.a.x, q.x.toFixed(1), JSON.stringify([u, o]));
    assert.equal(fg.label.a["text-anchor"], q.anchor);
  }
});
