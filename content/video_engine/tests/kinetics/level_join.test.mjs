// P71 T10 - THE LEVEL JOIN (the Bravos harvest v2's A9, rank 4; was P69 T39). One dashed rule at `from`'s level from
// the `from` datum to the far end's x, a dashed ring at each end, the gap written beside the far ring and never on the
// rule (C14). These tests pin the clock, the rule, the far end (a datum, or the value axis), the label's four places
// and the automatic side, the ring's yield to the page's words, the leave, and the painter reached only through ctx.
import { test } from "node:test";
import assert from "node:assert/strict";
import { LEVEL, levelPose, levelDashF, levelGlyphs, levelRuleD, levelFarEnd, levelLabelAt, levelRuleBand, levelOnRule,
         levelCost, levelSide, levelLeave, levelNudge, levelDashBox, levelDashYields, paintLevelJoin } from "../../scripts/species/level_join.mjs";
import { RING, ringEllipse, ringDashes } from "../../scripts/species/ring.mjs";

const near = (a, b, eps = 1e-6) => Math.abs(a - b) <= eps;
const sp = (o = {}) => Object.assign({ kind: "level_join", at: 10, dur: 2, from: 3, to: 9, label: "+5 pts" }, o);

test("the dials: the phases run in order inside the word, the figure is written last and lands with the word", () => {
  assert.ok(LEVEL.RING_A[0] === 0 && LEVEL.RING_A[1] < LEVEL.RULE[1], "the `from` ring lands as the rule leaves it");
  assert.ok(LEVEL.RULE[0] < LEVEL.RING_B[0] && LEVEL.RING_B[0] < LEVEL.RULE[1], "the far ring draws as the rule arrives");
  assert.ok(LEVEL.LABEL[0] >= LEVEL.RING_B[0] && LEVEL.LABEL[1] === 1, "the figure writes last and finishes on the word's end");
  assert.ok(LEVEL.RING_K > 0 && LEVEL.RING_K < 1, "an end ring is an END MARK, smaller than the ring species' callout");
  assert.ok(LEVEL.CLEAR_PX > 0 && LEVEL.PAD_PX > 0);
  assert.ok(LEVEL.FRAME_AIR_PX > 0, "inside a plot frame the figure keeps off the border");
});

test("the clock: nothing before the word; each phase 0..1 on its own window; all whole at the word's end", () => {
  assert.equal(levelPose(sp(), 9.99).on, false);
  const p0 = levelPose(sp(), 10);
  assert.equal(p0.on, true);
  assert.equal(p0.rule, 0);
  assert.equal(p0.label, 0);
  const pe = levelPose(sp(), 12);
  for (const k of ["ringA", "rule", "ringB", "label"]) assert.equal(pe[k], 1, k);
  const pm = levelPose(sp(), 10 + 2 * (LEVEL.RULE[0] + LEVEL.RULE[1]) / 2);
  assert.ok(near(pm.rule, 0.5, 1e-9), "the rule's min-jerk clock is symmetric: half its window is half its length");
  assert.ok(levelPose(sp(), 10 + 2 * LEVEL.RULE[0] + 0.05).rule < 0.05, "it leaves gently, never at speed");
});

test("the rule is a LEVEL: from A at A's height toward the far end's x, by length", () => {
  const A = [100, 300], E = [700, 250];
  assert.equal(levelRuleD(A, E, 0), null);
  assert.equal(levelRuleD(A, E, 1), "M100.0 300.0 L700.0 300.0", "horizontal at `from`'s level, to the far end's x");
  assert.equal(levelRuleD(A, E, 0.5), "M100.0 300.0 L400.0 300.0");
  assert.equal(levelRuleD([700, 300], [100, 250], 0.25), "M700.0 300.0 L550.0 300.0", "a join may run leftward");
  assert.equal(levelRuleD(null, E, 1), null);
});

test("the far end is the `to` datum, or - the axis form - the value axis at `from`'s level", () => {
  assert.deepEqual(levelFarEnd([100, 300], [700, 250], 40), [700, 250]);
  assert.deepEqual(levelFarEnd([100, 300], null, 40), [40, 300]);
  assert.equal(levelFarEnd([100, 300], null, NaN), null);
  assert.equal(levelFarEnd(null, null, 40), null);
});

const G = (o = {}) => Object.assign({ rx: 30, ry: 22, pad: 8, w: 120, fs: 26, dy: 0 }, o);

test("the label's four places sit beside the far ring, never on its centre; dy moves by lines of its own size", () => {
  const E = [500, 300], g = G();
  const r = levelLabelAt("right", E, g), l = levelLabelAt("left", E, g), a = levelLabelAt("above", E, g), b = levelLabelAt("below", E, g);
  assert.equal(r.anchor, "start"); assert.equal(r.x, 538); assert.ok(near(r.box[0], 538) && near(r.box[2], 658));
  assert.equal(l.anchor, "end"); assert.ok(near(l.box[2], 462) && near(l.box[0], 342));
  assert.equal(a.anchor, "middle"); assert.ok(near(a.box[3], 300 - 22 - 8), "above: its box ends a pad over the ring");
  assert.ok(near(b.box[1], 300 + 22 + 8), "below: its box starts a pad under the ring");
  assert.ok(near(levelLabelAt("right", E, G({ dy: 1 })).y - r.y, 26), "dy = one line of its own size");
});

test("C14: the label's box is tested against the rule's band - the rule's x span at its level, CLEAR either side", () => {
  const A = [100, 300], E = [700, 250];
  assert.deepEqual(levelRuleBand(A, E, 10), [100, 290, 700, 310]);
  assert.equal(levelOnRule([300, 280, 400, 305], A, E, 10), true, "a box crossing the level inside its span is ON the rule");
  assert.equal(levelOnRule([300, 250, 400, 285], A, E, 10), false, "clear above it");
  assert.equal(levelOnRule([720, 280, 800, 305], A, E, 10), false, "past the rule's end is not on it");
});

test("the automatic side is the first CLEAR one - right, the gap's own side, the other, left - and an authored side wins (s106)", () => {
  const A = [100, 300], E = [500, 250], base = G({ A, E, clear: 5, W: 1000, H: 560, boxes: [], pts: [] });
  assert.equal(levelSide(base, null), "right", "room to the right: it writes there");
  const tag = [530, 230, 900, 270];   /* an end tag beside the far datum */
  assert.equal(levelSide(Object.assign({}, base, { boxes: [tag] }), null), "above", "the far datum over the rule: above next");
  const low = Object.assign({}, base, { E: [500, 350], boxes: [[530, 330, 900, 370]] });
  assert.equal(levelSide(low, null), "below", "a far datum UNDER the rule: its own side is below");
  const edge = Object.assign({}, base, { W: 560 });
  assert.notEqual(levelSide(edge, null), "right", "the chart's edge is not room");
  assert.equal(levelSide(Object.assign({}, base, { boxes: [tag] }), "left"), "left", "the author's side stands");
  assert.equal(levelSide(base, "on"), "right", "an unknown side is not a side: the engine's own is used");
});

test("no side clear: the cheapest wins, and ON THE RULE costs most of all", () => {
  const A = [100, 300], E = [500, 300], g = G({ A, E, clear: 5, W: 1000, H: 560, pts: [] });
  const everywhere = [[0, 0, 1000, 290], [0, 312, 1000, 560], [520, 280, 1000, 320]];
  const s = levelSide(Object.assign({}, g, { boxes: everywhere }), null);
  assert.notEqual(s, "left", "left of a same-level far end is on the rule - never the fallback");
  assert.ok(levelCost(levelLabelAt("left", E, g).box, g) >= 1e6);
});

test("a ring dash that would stand on the page's own words is not drawn: the ring opens toward the word", () => {
  const e = ringEllipse({ x: 0, y: 0, w: 0, h: 0 }), dashes = ringDashes({ cx: 0, cy: 0, rx: e.rx * LEVEL.RING_K, ry: e.ry * LEVEL.RING_K });
  const boxes = dashes.map((d) => levelDashBox(d.d));
  assert.ok(boxes.every((b) => b[0] <= b[2] && b[1] <= b[3]));
  const right = boxes.filter((b) => levelDashYields(b, [500, 300], 2, [[505, 280, 700, 320]]));
  assert.ok(right.length > 0 && right.length < boxes.length, "only the dashes on the word's side yield");
  assert.equal(boxes.filter((b) => levelDashYields(b, [500, 300], 2, [])).length, 0);
});

test("the ring's dash law is the ring species' own (RING.DASH / DASH_GAP), at the end-mark scale", () => {
  assert.equal(RING.DASH, 26); assert.equal(RING.DASH_GAP, 15);
  const e = ringEllipse({ x: 0, y: 0, w: 0, h: 0 });
  assert.equal(e.rx, RING.MIN_RX); assert.equal(e.ry, RING.MIN_RY);
});

test("the glyphs write in order and the LAST one is whole when the window ends (R26-314)", () => {
  const n = 6;
  assert.deepEqual(levelGlyphs(0, n), [0, 0, 0, 0, 0, 0]);
  assert.deepEqual(levelGlyphs(1, n), [1, 1, 1, 1, 1, 1], "never a half-inked last letter");
  const m = levelGlyphs(0.5, n);
  assert.ok(m[0] === 1 && m[n - 1] === 0 && m.every((v, j) => j === 0 || v <= m[j - 1]));
});

test("the leave: an undraw's own clock takes it; none, it stands", () => {
  assert.equal(levelLeave(null, 50), 0);
  assert.equal(levelLeave({ at: 20, dur: 1 }, 19.9), 0);
  assert.equal(levelLeave({ at: 20, dur: 1 }, 21), 1);
  assert.ok(near(levelLeave({ at: 20, dur: 1 }, 20.5), 0.5, 1e-9));
});

/* ---- the painter, through ctx and recorders only ------------------------------------------------------------ */
const el = () => { const a = {}; return { a, setAttribute: (k, v) => { a[k] = String(v); }, getAttribute: (k) => a[k] }; };
const built = (o = {}) => {
  const ring = () => ({ g: el(), dashes: [0, 1, 2, 3, 4, 5].map((i) => ({ p: el(), t0: i / 6, t1: (i + 1) / 6, box: [-10, -10, 10, 10] })) });
  return Object.assign({ sp: sp(), si: 0, to: { si: 0, i: 9 }, g: el(), rule: el(), ringA: ring(), ringB: ring(), label: el(),
                         lg: [el(), el(), el()], side: "above", lg0: G(), k: 2, words: [], leave: null }, o);
};
const pts = { 3: [100, 300], 9: [700, 250] };
const ctx = { datumNow: (st, si, i) => (st.drop && st.drop === i ? null : pts[i] || null) };

test("the painter: hidden before its word, drawing through it, whole at its end - on the ACTIVE state's points", () => {
  const sd = built();
  paintLevelJoin(sd, 9.9, {}, ctx);
  assert.equal(sd.g.a.opacity, "0");
  paintLevelJoin(sd, 10 + 2 * 0.39, {}, ctx);
  assert.equal(sd.g.a.opacity, "1.000");
  const mid = sd.rule.a.d.match(/L([\d.]+) ([\d.]+)/);
  assert.ok(+mid[1] > 100 && +mid[1] < 700 && +mid[2] === 300, sd.rule.a.d);
  paintLevelJoin(sd, 12, {}, ctx);
  assert.equal(sd.rule.a.d, "M100.0 300.0 L700.0 300.0");
  assert.ok(sd.ringA.dashes.every((d) => d.p.a.opacity === "1") && sd.ringB.dashes.every((d) => d.p.a.opacity === "1"));
  assert.equal(sd.ringB.g.a.transform, "translate(700.0 250.0) scale(0.50000)", "the far ring on the far datum, 1/k");
  assert.ok(sd.lg.every((t) => t.a.opacity === "1.000"));
  assert.equal(sd.label.a["text-anchor"], "middle");
});

test("an end the window has dropped hides the join (R26-28); the axis form reads the builder's axis", () => {
  const sd = built();
  paintLevelJoin(sd, 12, { drop: 9 }, ctx);
  assert.equal(sd.g.a.opacity, "0");
  const ax = built({ to: { axis: true }, axisX: () => 40 });
  paintLevelJoin(ax, 12, {}, ctx);
  assert.equal(ax.rule.a.d, "M100.0 300.0 L40.0 300.0", "to the value axis at `from`'s level");
  assert.equal(ax.ringB.g.a.transform, "translate(40.0 300.0) scale(0.50000)");
});

test("the painter's leave, and a dash on the page's words stays undrawn", () => {
  const sd = built({ leave: { at: 20, dur: 1 } });
  paintLevelJoin(sd, 20.5, {}, ctx);
  assert.equal(sd.g.a.opacity, "0.500");
  paintLevelJoin(sd, 21.2, {}, ctx);
  assert.equal(sd.g.a.opacity, "0");
  const w = built({ words: [[695, 240, 900, 260]] });
  paintLevelJoin(w, 12, {}, ctx);
  assert.ok(w.ringB.dashes.every((d) => d.p.a.opacity === "0"), "every dash box here overlaps the word: all yield");
  assert.ok(w.ringA.dashes.every((d) => d.p.a.opacity === "1"), "the other ring is untouched");
});

test("inside a plot frame every side is nudged in - left / up first - and a page with no frame is untouched", () => {
  const E = [990, 300], g = G(), frame = [70, 40, 1000, 458];
  const bare = levelLabelAt("above", E, g), inF = levelLabelAt("above", E, Object.assign({}, g, { frame, air: 4 }));
  assert.ok(bare.box[2] > 996, "the flat face: centred on the ring, past the frame's edge - as it was");
  assert.ok(near(inF.box[2], 996) && near(inF.box[1], bare.box[1]) && inF.inside, "nudged LEFT to 4 inside the border");
  assert.ok(near(inF.x - bare.x, inF.box[0] - bare.box[0]), "the text moves with its box");
  const top = levelLabelAt("above", [500, 60], Object.assign({}, g, { frame, air: 4 }));
  assert.ok(near(top.box[1], 44), "past the top: moved DOWN to 4 inside it");
  assert.deepEqual(levelNudge([0, 0, 10, 10], null, 4), { dx: 0, dy: 0, inside: true });
  assert.equal(levelNudge([0, 0, 2000, 10], frame, 4).inside, false, "wider than the frame: reported, aligned left");
});
