// P57 T20 / R26-98 - THE FIGURE PROMOTED (the P55 T7 recipe), a PAGE painter. The promotion's proof is that
// every golden is byte-identical, so what this file pins is that the module still carries the INLINE ENGINE's
// numbers and arithmetic: R26-71's step-off (the box, the quanta, the side `dy` chose, the caps), the authored
// place both the BUILDER and the PAINTER now read through one function, and the hand's write clock - the figure
// over the first 0.6 of the word, the sub over the rest, each glyph with the 1.6 overlap. The painter is called
// on recorders with no DOM: it reaches the engine only through its page ctx (markDatum, pointsNow, PS).
import { test } from "node:test";
import assert from "node:assert/strict";
import { FIGURE, segMeetsBox, boxMeetsBox, figBox, figWidth, figClearY, figurePlace, figureGlyph, figureSubGlyph,
         paintFigure } from "../../scripts/species/figure.mjs";

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
                 clamp01((0.9 - 0.6 - 1 * (0.4 / 2)) / ((0.4 / 2) * 1.6))), "the inline expression");
  /* the same overrun, and the SUB has no room after it to finish in: `u` is clamped at 1, so the last glyph of
     a sub holds at 0.625 from the end of the word on. That is what the inline engine has always painted - it is
     recorded here, not corrected: a value change is a golden change, and this promotion changes no pixel. */
  assert.ok(near(figureSubGlyph(1, 1, 2), 0.625), "the sub's last glyph holds at 0.625 - the inline tail");
  assert.equal(figureSubGlyph(1, 0, 2), 1, "every glyph before it is fully in");
});

// ---------------------------------------------------------------- the painter, on recorders, with no DOM
test("the painter writes the glyph opacities to three places, and nothing before the word", () => {
  const fg = built();
  paintFigure(fg, 9, null, { PS });
  assert.equal(fg.g.a.opacity, 0, "t < at: nothing on the page");
  paintFigure(fg, 12, null, { PS });
  assert.equal(fg.g.a.opacity, 1);
  assert.deepEqual(fg.lg.map((n) => n.a.opacity), ["1.000", "1.000", "1.000", "1.000"]);
  assert.deepEqual(fg.sg.map((n) => n.a.opacity), ["1.000", "0.625"], "the sub's tail, as the inline code paints it");
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
