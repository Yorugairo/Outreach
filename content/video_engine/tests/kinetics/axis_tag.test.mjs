// P71 T9 - THE AXIS TAG and its DROP GUIDE (the Bravos harvest v2's A10, rank 3; A42 / A43 the same pill). The named
// year becomes an accent pill IN its tick's place (HIS 05:52, JPN 01:16) and a pill wider than one tick covers its
// neighbours (BOOM "November 1999"); on a line page a dotted guide drops from the datum to the pill, never across a
// label (C14). These tests pin the pop, the covering rule, the guide's runs, the live place (R26-28) and the painter
// reached only through ctx.
import { test } from "node:test";
import assert from "node:assert/strict";
import { AXTAG, axtagPose, axtagStart, axtagPillBox, axtagRect, axtagOverlaps, axtagContains, axtagHides, axtagCoverScale,
         axtagGuideRuns, axtagGuideD, axtagLabelBox, axtagPlace, paintAxisTags } from "../../scripts/species/axis_tag.mjs";
import { TIPPILL, pillBox } from "../../scripts/species/tippill.mjs";
import { BREAK } from "../../scripts/species/breakthrough.mjs";

const near = (a, b, eps = 1e-6) => Math.abs(a - b) <= eps;
const sp = (o = {}) => Object.assign({ kind: "axis_tag", at: 10, dur: 0.9, x: 2000 }, o);

test("the dials are tippill's pill and the capsule's dotted leader, by value (tippill's region sits after paintPerform)", () => {
  assert.equal(AXTAG.PAD_X, TIPPILL.PAD_X);
  assert.equal(AXTAG.PAD_Y, TIPPILL.PAD_Y);
  assert.equal(AXTAG.POP_MP, TIPPILL.POP_MP, "R26-34's named overshoot for a pill that arrives on a word");
  assert.equal(AXTAG.GUIDE_DASH, BREAK.CAP_LEAD_DASH, "dotted: a solid rule across a chart is a comparator (E53 s6)");
  assert.equal(AXTAG.GUIDE_W, BREAK.CAP_LEAD_W);
  assert.equal(AXTAG.GUIDE_GAP, BREAK.CAP_LEAD_GAP);
  assert.equal(AXTAG.MAX_STANDING, 3, "the don't: more than 2-3 tags in one hold (USE-WHEN :323)");
  assert.ok(AXTAG.TYPE_K > 1, "the pill's type is bolder than the tick it replaces");
  assert.ok(AXTAG.GUIDE_AT + AXTAG.GUIDE_S <= 0.4 && AXTAG.POP_S <= 0.4, "pill and guide have landed 0.4 s after the word");
});

test("the pill's box is tippill's pillBox for the same text", () => {
  for (const [w, h] of [[60, 30], [210, 37.5], [0, 24]]) {
    const a = axtagPillBox(w, h), b = pillBox(w, h);
    for (const k of ["w", "h", "x", "y", "r"]) assert.ok(near(a[k], b[k]), `${k} ${a[k]} vs ${b[k]}`);
  }
});

// ---------------------------------------------------------------- the pop
test("THE POP: nothing before the word, then springPop about the centre; the guide drops after it", () => {
  const p0 = axtagPose(sp(), 9.99), p1 = axtagPose(sp(), 10), pe = axtagPose(sp(), 10 + AXTAG.POP_S), pz = axtagPose(sp(), 14);
  assert.equal(p0.on, false);
  assert.equal(p0.s, 0);
  assert.equal(p1.on, true);
  assert.equal(p1.s, 0);
  assert.equal(pe.s, 1);
  assert.equal(pz.s, 1, "it STANDS: the tag holds after its word");
  let peak = 0;
  for (let k = 1; k < 50; k++) peak = Math.max(peak, axtagPose(sp(), 10 + (AXTAG.POP_S * k) / 50).s);
  assert.ok(peak > 1 && peak < 1.1, "one notch of overshoot, never a bounce: " + peak);
  assert.equal(axtagPose(sp(), 10 + AXTAG.GUIDE_AT).guide, 0);
  assert.equal(axtagPose(sp(), 10 + AXTAG.GUIDE_AT + AXTAG.GUIDE_S).guide, 1);
  assert.ok(near(axtagPose(sp(), 10 + AXTAG.GUIDE_AT + AXTAG.GUIDE_S / 2).guide, 0.5), "min-jerk: half the time, half the length");
});

test("THE POP WAITS FOR ITS PAGE: a word spoken while its state is still arriving pops when the state stands", () => {
  const recast = { kind: "chart_to", at: 80.49, dur: 1.2, to: "recast", state: 1 };
  assert.equal(axtagStart(sp({ at: 80.5 }), [recast]), 80.49 + 1.2, "H row 9: the GDP page stands at 81.69, not on the word");
  assert.equal(axtagStart(sp({ at: 82.5 }), [recast]), 82.5, "a word after the page has arrived is the pop's own start");
  assert.equal(axtagStart(sp({ at: 10 }), []), 10, "a page with no states: the word");
  assert.equal(axtagStart(sp({ at: 80.5 }), [recast, { kind: "chart_to", at: 80.6, dur: 1, to: "park" }]), 80.49 + 1.2,
    "a park or a compare changes no state");
  assert.equal(axtagStart(sp({ at: 80.5 }), [{ ...recast, keyed: "data" }], 1.6), 80.49 + 1.6, "a keyed data recast runs at least its floor");
  assert.equal(axtagStart(sp({ at: 80.4 }), [recast]), 80.4, "a verb after the word does not delay it");
  const late = axtagPose(sp({ at: 80.5 }), 81.0, 81.69);
  assert.equal(late.on, false, "nothing under the hand-over");
  assert.equal(axtagPose(sp({ at: 80.5 }), 81.69 + AXTAG.POP_S, 81.69).s, 1, "the pop runs on its own clock from the arrival");
});

test("a seek IS the play: the same t gives the same pose in any order", () => {
  const ts = [10.02, 10.31, 9.5, 10.02, 12, 10.31];
  const a = ts.map((t) => JSON.stringify(axtagPose(sp(), t)));
  const b = [...ts].reverse().map((t) => JSON.stringify(axtagPose(sp(), t))).reverse();
  assert.deepEqual(a, b);
});

// ---------------------------------------------------------------- replaces or covers
test("THE COVERING RULE: the named tick hides once the pill CONTAINS it, a neighbour the moment the pill reaches it", () => {
  const pill = axtagPillBox(80, 30), tick = [480, 590, 50, 20], nb = [555, 590, 50, 20];
  const small = axtagRect(505, 600, pill, 0.3), whole = axtagRect(505, 600, pill, 1);
  assert.equal(axtagHides(small, tick, true), false, "a sliver of pill: the tick still shows round it (HIS 05:52)");
  assert.equal(axtagHides(whole, tick, true), true, "the pill has swallowed it: the tick BECAME the pill");
  assert.equal(axtagOverlaps(small, nb), false);
  assert.equal(axtagHides(whole, nb, false), true, "a neighbour under the pill's edge is covered (BOOM: November 1999 over 1998-2000)");
  assert.equal(axtagHides(whole, [700, 590, 50, 20], false), false, "a tick the pill never reaches keeps its label");
  const sc = axtagCoverScale(505, 600, pill, tick);
  assert.ok(sc > 0.3 && sc < 1);
  assert.equal(axtagContains(axtagRect(505, 600, pill, sc + 1e-9), tick), true, "the cover scale is exact");
  assert.equal(axtagContains(axtagRect(505, 600, pill, sc - 1e-3), tick), false);
  assert.equal(axtagCoverScale(505, 600, pill, null), 0);
});

// ---------------------------------------------------------------- the guide
test("THE GUIDE is cut round every label it would cross (C14), and a label beside it cuts nothing", () => {
  assert.deepEqual(axtagGuideRuns(500, 100, 400, []), [[100, 400]]);
  const runs = axtagGuideRuns(500, 100, 400, [[450, 200, 100, 30], [700, 250, 100, 30]], 6);
  assert.deepEqual(runs, [[100, 194], [236, 400]]);
  assert.deepEqual(axtagGuideRuns(500, 100, 400, [[400, 0, 200, 500]]), [], "a label over the whole run: no guide at all");
  assert.deepEqual(axtagGuideRuns(500, 400, 100, []), [], "a pill above its datum has no room for a drop");
  assert.equal(axtagGuideD(500, [[100, 194], [236, 400]], 300), "M500.0 100.0 L500.0 194.0 M500.0 236.0 L500.0 300.0",
    "drawn DOWN by length from the datum: the second run is only drawn to 300");
  assert.equal(axtagGuideD(500, [[100, 194], [236, 400]], 150), "M500.0 100.0 L500.0 150.0");
  assert.equal(axtagGuideD(500, [], 150), "");
});

// ---------------------------------------------------------------- the painter
const rec = (a0 = {}) => { const a = { ...a0 }; return { a, setAttribute: (k, v) => { a[k] = String(v); }, getAttribute: (k) => a[k] ?? null, style: {} }; };
const lab = (x, top = 590, w = 50, h = 20) => ({ el: rec({ x: String(x) }), w, h, top, anchor: "middle", hid: false });
/* a series' stroke drawn to its end: litDrawnX reads its dash */
const stroke = (xEnd) => ({ si: 0, len: 100, p: { style: {}, getAttribute: () => "0", getPointAtLength: () => ({ x: xEnd }) } });
const setup = (o = {}) => {
  const named = lab(500), left = lab(420), right = lab(580);
  const td = { sp: sp(o.sp || {}), g: rec(), rect: rec(), text: rec(), guide: rec(), pill: axtagPillBox(80, 30),
               on: [{ si: 0, di: 120, label: named, cy: 600 }] };
  const at = { tags: [td], labels: [left, named, right], boxesOf: [o.boxes || []], leaveOf: o.leaveOf };
  const st = { paths: [stroke(o.drawn == null ? 900 : o.drawn)] };
  return { td, at, st, named, left, right };
};
const ctxAt = (p) => ({ datumNow: () => p });

test("THE PAINTER: nothing before the word; the pill pops at the datum's x on the tick row; the text waits for the cover", () => {
  const { td, at, st, named, left } = setup();
  const ctx = ctxAt([500, 300]);
  paintAxisTags(at, 9.9, st, ctx);
  assert.equal(td.g.a.opacity, "0");
  assert.equal(named.el.style.visibility, undefined, "no tick is touched before the word");
  paintAxisTags(at, 10.02, st, ctx);   /* early in the pop: a sliver */
  assert.match(td.g.a.transform, /^translate\(500\.0 600\.0\) scale\(/);
  assert.equal(td.text.a.opacity, "0.000", "the text never stands on the tick it replaces (M28)");
  assert.equal(named.el.style.visibility, undefined, "the tick shows round the sliver");
  paintAxisTags(at, 10 + AXTAG.POP_S, st, ctx);   /* landed */
  assert.equal(td.g.a.transform, "translate(500.0 600.0) scale(1.0000)");
  assert.equal(td.text.a.opacity, "1.000");
  assert.equal(named.el.style.visibility, "hidden", "the tick has BECOME the pill");
  assert.equal(left.el.style.visibility, undefined, "a neighbour the pill does not reach keeps its label");
});

test("THE GUIDE draws by length from the datum down to the pill's top, and not ahead of the ink", () => {
  const { td, at, st } = setup();
  const ctx = ctxAt([500, 300]);
  paintAxisTags(at, 10 + AXTAG.GUIDE_AT + AXTAG.GUIDE_S, st, ctx);
  const y0 = 300 + AXTAG.GUIDE_GAP, y1 = 600 - td.pill.h / 2 - AXTAG.GUIDE_GAP;
  assert.equal(td.guide.a.d, `M500.0 ${y0.toFixed(1)} L500.0 ${y1.toFixed(1)}`);
  assert.equal(td.guide.a.opacity, "1.000");
  paintAxisTags(at, 10 + AXTAG.GUIDE_AT + AXTAG.GUIDE_S / 2, st, ctx);
  assert.equal(td.guide.a.d, `M500.0 ${y0.toFixed(1)} L500.0 ${(y0 + (y1 - y0) / 2).toFixed(1)}`, "half the time: half the drop");
  const un = setup({ drawn: 300 });
  paintAxisTags(un.at, 12, un.st, ctx);
  assert.equal(un.td.guide.a.opacity, "0", "the line has not reached the datum: no guide to it");
  const off = setup({ sp: { guide: false } });
  paintAxisTags(off.at, 12, off.st, ctx);
  assert.equal(off.td.guide.a.opacity, "0", "guide: false - the pill alone");
  const cut = setup({ boxes: [[450, 400, 100, 30]] });
  paintAxisTags(cut.at, 12, cut.st, ctx);
  assert.equal(cut.td.guide.a.d.split("M").length - 1, 2, "C14: the guide is cut round the label it would cross");
});

test("IT FOLLOWS THE LIVE SCALE (R26-28): the datum moves, the pill and the guide move with it; a dropped datum hides it", () => {
  const { td, at, st } = setup();
  paintAxisTags(at, 12, st, ctxAt([500, 300]));
  assert.match(td.g.a.transform, /^translate\(500\.0 /);
  paintAxisTags(at, 12, st, ctxAt([640, 250]));
  assert.match(td.g.a.transform, /^translate\(640\.0 600\.0\)/);
  assert.match(td.guide.a.d, /^M640\.0 256\.0 /);
  paintAxisTags(at, 12, st, ctxAt(null));
  assert.equal(td.g.a.opacity, "0", "the window dropped the datum: nothing drawn in the wrong place");
});

test("A COVERED LABEL COMES BACK: the page's leave fades the pill and gives the ticks back when it has gone", () => {
  let lv = 0;
  const { td, at, st, named } = setup({ leaveOf: () => lv });
  paintAxisTags(at, 12, st, ctxAt([500, 300]));
  assert.equal(named.el.style.visibility, "hidden");
  lv = 0.5;
  paintAxisTags(at, 12.5, st, ctxAt([500, 300]));
  assert.equal(td.g.a.opacity, "0.500");
  assert.equal(named.el.style.visibility, "hidden", "the pill still covers it while it fades");
  lv = 1;
  paintAxisTags(at, 13, st, ctxAt([500, 300]));
  assert.equal(td.g.a.opacity, "0");
  assert.equal(named.el.style.visibility, "", "given back");
  paintAxisTags(at, 9, st, ctxAt([500, 300]));
  assert.equal(named.el.style.visibility, "", "and a seek back before the word leaves it alone");
});

test("A BARS TAG stands under its bar and draws no guide; a WIDE pill covers the neighbour its edge reaches", () => {
  const named = lab(500), right = lab(560);
  const td = { sp: sp({ x: 3, label: "Nvidia and friends" }), g: rec(), rect: rec(), text: rec(), guide: rec(),
               pill: axtagPillBox(160, 30), on: [{ si: 0, di: 3, label: named, cy: 600, bars: true }] };
  const at = { tags: [td], labels: [named, right], boxesOf: [[]] };
  paintAxisTags(at, 12, { paths: [] }, ctxAt([500, 200]));
  assert.equal(td.guide.a.opacity, "0", "a guide down a bar is a seam in it");
  assert.equal(named.el.style.visibility, "hidden");
  assert.equal(right.el.style.visibility, "hidden", "covered by the wide pill");
});

test("axtagPlace answers null on a state that does not carry the value, and reads the state the page is on", () => {
  const named = lab(500);
  const td = { on: [null, { si: 0, di: 7, label: named, cy: 610 }] };
  const st = { states: [{ paths: [] }, { paths: [] }], active: 0 };
  assert.equal(axtagPlace(td, st, ctxAt([1, 2])), null, "state 0 (the railway page) has no 2000");
  st.active = 1;
  const P = axtagPlace(td, st, ctxAt([333, 222]));
  assert.equal(P.x, 333);
  assert.equal(P.y, 222);
  assert.equal(P.cy, 610);
  assert.equal(P.k, 1);
  assert.deepEqual(axtagLabelBox(named), [475, 590, 50, 20]);
});

test("the painter reaches the engine ONLY through ctx and its state - no clock, no random, no DOM of its own", async () => {
  const { readFile } = await import("node:fs/promises");
  const src = await readFile(new URL("../../scripts/species/axis_tag.mjs", import.meta.url), "utf-8");
  for (const bad of ["Date.now", "performance.now", "Math.random", "document.", "window.", "requestAnimationFrame"]) {
    assert.ok(!src.includes(bad), bad);
  }
  assert.match(src.split(/\r?\n/)[0], /^\/\* SPACE: page \*\/$/);   // a Windows checkout is CRLF
  assert.match(src.trimEnd().split(/\r?\n/).pop(), /PAGE_PAINTERS\.axis_tag = paintAxisTags;$/);
});
