// R26-191 (E99 s75) - THE VALUE ROW THAT WILL NOT FIT: INSIDE ITS OWN BAR, OR THINNED - never mirrored
// across the zero line, and never into the tick band. The operator on the weak-prints page (2026-09-17):
// "why are we still colliding ont he charts with labels and axes?" / "yeah, still colliding. doesn't seem
// like aynthing changed"; the parent, on the first build of this law: a drop's number above the line and the
// rise's below it is E28 backwards - sign is geometry, and a label's side of the line is part of its sign.
//
// The numbers below are the weak-prints page (`ledger:ev-weak-prints-v1:bars:7`) MEASURED off its own live
// DOM at t = 44.16 in the private build `build-p66-cal-labels` (the chart's viewBox is 0 0 800 433, drawn
// 1:1 in stage px), so this file is the 0:44 frame's arithmetic and not a re-typed idea of it.
import { test } from "node:test";
import assert from "node:assert/strict";
import { LF, lfRgb, lfLum, lfContrast, lfOnInk, lfSplitRow, lfThinRow, lfTickYear, lfTickKeep } from "../../scripts/kinetics/labelfit.mjs";

// ---- the page, measured ---------------------------------------------------------------------------------
const SIZE = 40, ASC = 0.92, DESC = 0.18;            // LPVAL.ASC / LPVAL.LAB_DESC, the engine's own dials
const BOX_H = (ASC + DESC) * SIZE;                   // 44.0 - what an overlap gate measures
const PAGE = { base: 221, top: 150, bottom: 363 };   // the zero line, the plot's top, the plot's floor
const TICK_TOP = 415 - ASC * SIZE;                   // 378.2 - the top of the month row's own boxes
const ORANGE = "rgb(255, 138, 76)";                  // E67's crimson slot (#FF8A4C), bars 0-4, 6, 7
const TEAL = "rgb(52, 245, 197)";                    // E67's teal (#34F5C5), bar 5 - the one that rose
const CHAR = "#25313C", CREAM = "#F4E6C7";           // the board's own two inks (E22), declared on `.lp`
const INKS = [CHAR, CREAM];
const VAL_INK = "#c9ced4";                           // .val on the charcoal field
const BW = 51.1;                                     // EVERY bar on this page is 51.1 units wide ...
// i, value, height, the bar's centre x, the label and its measured width (... and the widest is 126.75)
const BARS = [
  { i: 0, v: -3.9, h: 18.5, cx: 188.75, s: "-3.9%", w: 104.50, fill: ORANGE },
  { i: 1, v: -12.4, h: 58.7, cx: 266.25, s: "-12.4%", w: 126.75, fill: ORANGE },
  { i: 2, v: -5.3, h: 25.1, cx: 343.75, s: "-5.3%", w: 104.50, fill: ORANGE },
  { i: 3, v: -10.5, h: 49.7, cx: 421.25, s: "-10.5%", w: 126.75, fill: ORANGE },
  { i: 4, v: -11.3, h: 53.5, cx: 498.75, s: "-11.3%", w: 126.75, fill: ORANGE },
  { i: 5, v: 10.9, h: 51.6, cx: 576.25, s: "10.9%", w: 113.42, fill: TEAL },
  { i: 6, v: -8.7, h: 41.2, cx: 653.75, s: "-8.7%", w: 104.50, fill: ORANGE },
  { i: 7, v: -13.8, h: 65.3, cx: 731.25, s: "-13.8%", w: 126.75, fill: ORANGE, badge: true },
];
// the month row as the page writes it, and as it measures after the first tick yields its year
const MONTHS = [["Oct '24", 125.47], ["Dec", 71.14], ["Jan", 64.50], ["Feb", 68.94], ["Mar", 68.89],
                ["Jun", 64.50], ["Jul", 51.14], ["Jul '26", 114.38]];
const OCT_W = 62.23;                                 // "Oct" measured in the page's own face at 40 px
const tickBoxes = (first = MONTHS[0][1]) => MONTHS.map(([, w], i) => [BARS[i].cx - (i ? w : first) / 2, i ? w : first]);
const PILL = { role: "pill", s: "-13.8%", box: [623, 2.5, 223, 85] };   // the risen badge at 0:44

const tipOf = (b) => (b.v < 0 ? PAGE.base + b.h : PAGE.base - b.h);
const boxAt = (b, y) => [b.cx - b.w / 2, y - ASC * SIZE, b.w, BOX_H];   // a value's box from its baseline y
const authoredY = (b) => (b.v < 0 ? tipOf(b) + 62 : tipOf(b) - 22);     // the builder's own portrait places
const place = (b) => lfSplitRow({ base: PAGE.base, end: tipOf(b), neg: b.v < 0, size: SIZE, asc: ASC,
                                  desc: DESC, bw: b.bw == null ? BW : b.bw, labW: b.w,
                                  reads: !!lfOnInk(b.fill, INKS) });
const inRect = (box, y0, y1) => box[1] >= y0 - 1e-9 && box[1] + box[3] <= y1 + 1e-9;
// the gate's own arithmetic (probe.py LABEL_TOUCH_PX 2, LABEL_LEAD_SHARE 0.18): two boxes MEET when they
// overlap by more than a hairline on both axes and by more than the shorter box's own leading.
const meets = (a, b) => {
  const ox = Math.min(a[0] + a[2], b[0] + b[2]) - Math.max(a[0], b[0]);
  const oy = Math.min(a[1] + a[3], b[1] + b[3]) - Math.max(a[1], b[1]);
  return ox > 2 && oy > 2 && oy > 0.18 * Math.min(a[3], b[3]);
};

// ---- 1. the arithmetic this file rests on ---------------------------------------------------------------
test("the WCAG helper is right at both ends of the scale, and reads every colour form the DOM hands back", () => {
  assert.ok(Math.abs(lfContrast("#FFFFFF", "#000000") - 21) < 1e-9, "white on black is 21:1");
  assert.ok(Math.abs(lfContrast(CHAR, CHAR) - 1) < 1e-12, "a colour on itself is 1:1");
  assert.deepEqual(lfRgb("#FF8A4C"), [255, 138, 76]);
  assert.deepEqual(lfRgb("rgb(255, 138, 76)"), [255, 138, 76], "getComputedStyle's own form");
  assert.deepEqual(lfRgb("rgba(255, 138, 76, 0.5)"), [255, 138, 76]);
  assert.deepEqual(lfRgb("#f84"), [255, 136, 68], "the short hex");
  assert.equal(lfRgb("var(--lp-neg)"), null, "an unresolved var is not a colour - the caller must not go inside");
  assert.equal(lfRgb("none"), null);
  assert.equal(lfContrast("none", CHAR), null);
  assert.ok(Math.abs(lfLum("#000000")) < 1e-12 && Math.abs(lfLum("#FFFFFF") - 1) < 1e-12);
});

test("the ink that goes INSIDE a bar is measured on the bar's own fill, and 4.5:1 is a floor, not a wish", () => {
  const onOrange = lfOnInk(ORANGE, INKS);
  assert.equal(onOrange.ink, CHAR, "the charcoal reads on the E67 orange; the cream does not");
  assert.ok(Math.abs(onOrange.ratio - 5.68) < 0.02, `orange/charcoal measured ${onOrange.ratio}`);
  assert.ok(lfContrast(CREAM, ORANGE) < 3, `the cream on the orange is only ${lfContrast(CREAM, ORANGE).toFixed(2)}:1`);
  const onTeal = lfOnInk(TEAL, INKS);
  assert.equal(onTeal.ink, CHAR);
  assert.ok(Math.abs(onTeal.ratio - 9.48) < 0.02, `teal/charcoal measured ${onTeal.ratio}`);   // CAPABILITIES.md:34 says 9.5:1
  // the page's own value ink would vanish on both - which is WHY an inside label is re-inked, and why a
  // label that stays on the FIELD keeps that grey (8.4:1 on the charcoal E22 ground)
  assert.ok(lfContrast(VAL_INK, ORANGE) < 1.6 && lfContrast(VAL_INK, TEAL) < 1.6);
  assert.ok(Math.abs(lfContrast(VAL_INK, "#25313C") - 8.38) < 0.02);
  assert.equal(lfOnInk("#808080", INKS), null, "both inks are under 4.5:1 on a mid grey");
  assert.equal(lfOnInk("nonsense", INKS), null);
  assert.equal(LF.MIN_RATIO, 4.5);
  assert.ok(lfOnInk("#808080", INKS, 3) !== null, "the floor is a parameter, and 4.5 is the default");
});

// ---- 2. inside, or nothing - and never on the wrong side of the line ------------------------------------
test("R26-191: a bar HOLDS the number or it does not get it - inside, flush on the zero-line edge", () => {
  const wide = { base: PAGE.base, end: PAGE.base + 60, neg: true, size: SIZE, asc: ASC, desc: DESC,
                 bw: 140, labW: 126.75, reads: true };
  const p = lfSplitRow(wide);
  assert.equal(p.where, "inside");
  assert.ok(Math.abs(p.y - 257.8) < 1e-9, `the baseline is flush on the zero-line edge, measured ${p.y}`);
  const box = [0, p.y - ASC * SIZE, 126.75, BOX_H];
  assert.ok(inRect(box, PAGE.base, PAGE.base + 60), "the whole box is inside the bar's rect");
  assert.ok(Math.abs(box[1] - PAGE.base) < 1e-9, "flush on the baseline edge - the end the other row is furthest from");
  assert.ok(Math.abs(p.y - LF.CAP * SIZE - PAGE.base - (ASC - LF.CAP) * SIZE) < 1e-9,
            "the cap band stands 0.20 em of the bar's own fill off the zero line - the type's own air, not a new dial");
  const up = lfSplitRow({ ...wide, neg: false, end: PAGE.base - 60 });
  assert.equal(up.where, "inside");
  assert.ok(Math.abs(up.y - 213.8) < 1e-9, "a RISE is the mirror INSIDE ITS OWN BAR: the box's bottom flush on the line");
  // one unit too narrow, one unit too short, or an ink that does not read, and nothing goes in
  assert.equal(lfSplitRow({ ...wide, bw: 126.74 }).where, "thin", "the number must fit the bar it is written on");
  assert.equal(lfSplitRow({ ...wide, end: PAGE.base + BOX_H - 0.1 }).where, "thin");
  assert.equal(lfSplitRow({ ...wide, bw: undefined }).where, "thin", "a width it did not measure is not a width");
  assert.equal(lfSplitRow({ ...wide, reads: false }).where, "thin", "a bar no ink reads on is not a place for a number");
  assert.equal(lfSplitRow({ ...wide, bw: 10 }).y, null, "and `thin` never answers a y - there is no second place");
});

test("E28: no label this law places is ever on the wrong side of the zero line", () => {
  for (const neg of [true, false]) {
    for (const h of [44, 60, 120, 300]) {
      const p = lfSplitRow({ base: PAGE.base, end: neg ? PAGE.base + h : PAGE.base - h, neg, size: SIZE,
                             asc: ASC, desc: DESC, bw: 200, labW: 100, reads: true });
      assert.equal(p.where, "inside");
      const box = [0, p.y - ASC * SIZE, 100, BOX_H];
      assert.ok(neg ? box[1] >= PAGE.base - 1e-9 : box[1] + box[3] <= PAGE.base + 1e-9,
                `a ${neg ? "drop" : "rise"}'s number crossed the zero line - sign is geometry (E28)`);
    }
  }
});

// ---- 3. the weak-prints page at 0:44: the row THINS ------------------------------------------------------
test("R26-191b: the page's bars are too NARROW to hold their numbers, so the ROW THINS - min, max and last", () => {
  for (const b of BARS) assert.ok(BW < b.w, `bar ${b.i} is ${BW} wide and "${b.s}" is ${b.w}`);
  for (const b of BARS.filter((x) => (x.i & 1) === 1)) assert.equal(place(b).where, "thin", `bar ${b.i}`);
  const keep = lfThinRow(BARS.map((b) => b.v));
  assert.deepEqual(keep, [5, 7], "the maximum (+10.9), and the minimum (-13.8) which is also the last bar");
  assert.ok(BARS[7].badge, "and the last bar is the one the badge points at");
  assert.deepEqual(lfThinRow([4, 9, 2, 7]), [1, 2, 3], "max, min, last");
  assert.deepEqual(lfThinRow([5, 5, 1]), [0, 2], "a tie goes to the first bar that holds it");
  assert.deepEqual(lfThinRow([]), []);
  assert.deepEqual(lfThinRow([3]), [0]);
});

test("R26-191b: every kept label stays on ITS OWN SIGN SIDE, where the unsplit path put it, and out of the band", () => {
  const keep = new Set(lfThinRow(BARS.map((b) => b.v)));
  const shown = [];
  for (const b of BARS) {
    if (!keep.has(b.i)) continue;                      // the rest are not printed at all - the axis has the scale
    const box = boxAt(b, authoredY(b));                // NOTHING moves: the survivors keep the authored place
    assert.ok(b.v < 0 ? box[1] >= PAGE.base : box[1] + box[3] <= PAGE.base,
              `val:${b.s} crossed the zero line - E28: a drop's number sits with the drop`);
    assert.ok(box[1] + box[3] <= TICK_TOP, `val:${b.s} reached the month-tick band`);
    shown.push({ role: "val", s: b.s, box });
  }
  assert.deepEqual(shown.map((l) => l.s), ["10.9%", "-13.8%"]);
  const ticks = tickBoxes(OCT_W).map(([x, w], i) => ({ role: "tick", s: MONTHS[i][0], box: [x, TICK_TOP, w, BOX_H] }))
                                .filter((t, i) => lfTickKeep(tickBoxes(OCT_W))[i]);
  const all = [...shown, ...ticks, PILL];
  for (let i = 0; i < all.length; i++) {
    for (let j = i + 1; j < all.length; j++) {
      assert.ok(!meets(all[i].box, all[j].box),
                `${all[i].role}:${all[i].s} meets ${all[j].role}:${all[j].s} - ${JSON.stringify(all[i].box)} ${JSON.stringify(all[j].box)}`);
    }
  }
  // and the numbers the page no longer prints are exactly the six the old split threw into the bands
  const gone = BARS.filter((b) => !keep.has(b.i)).map((b) => b.s);
  assert.deepEqual(gone, ["-3.9%", "-12.4%", "-5.3%", "-10.5%", "-11.3%", "-8.7%"]);
});

// ---- 4. the tick row: two labels never touch -------------------------------------------------------------
test("R26-191b: the FIRST tick yields its year, and the LAST tick never yields at all", () => {
  assert.deepEqual(lfTickYear("Oct '24"), { base: "Oct", year: "'24" });
  assert.deepEqual(lfTickYear("Jul '26"), { base: "Jul", year: "'26" });
  assert.deepEqual(lfTickYear("Q3 2024"), { base: "Q3", year: "2024" });
  assert.equal(lfTickYear("Dec"), null);
  assert.equal(lfTickYear("2024"), null, "a tick that is ONLY a year keeps it - there is nothing else to read");
  assert.equal(lfTickYear(""), null);

  const full = lfTickKeep(tickBoxes());               // the row as the page writes it
  assert.deepEqual(full, [true, false, true, true, true, true, false, true],
                   "Oct '24 on Dec: the later yields; Jul on Jul '26: the LAST stays, so its neighbour goes");
  const yielded = lfTickKeep(tickBoxes(OCT_W));       // ... and after "Oct '24" -> "Oct"
  assert.deepEqual(yielded, [true, true, true, true, true, true, false, true],
                   "the year alone saves Dec; only Jul still touches Jul '26");
  assert.equal(yielded.filter((k) => !k).length, 1, "one month yields, not half the row");
  // no two kept labels touch, by the gate's own hairline
  const kept = tickBoxes(OCT_W).filter((b, i) => yielded[i]);
  for (let i = 1; i < kept.length; i++) {
    assert.ok(kept[i][0] - (kept[i - 1][0] + kept[i - 1][1]) >= -2,
              `${MONTHS[i][0]} still touches its neighbour`);
  }
});

test("R26-191b: a row no gate would fault is returned untouched - the hairline is the gate's own", () => {
  const clear = [[0, 50], [60, 50], [120, 50]];
  assert.deepEqual(lfTickKeep(clear), [true, true, true]);
  const hair = [[0, 50], [48, 50]];                   // 2 units of overlap: the probe's own hairline
  assert.deepEqual(lfTickKeep(hair), [true, true], "2 px is a hairline, not a touch (probe.py LABEL_TOUCH_PX)");
  assert.deepEqual(lfTickKeep([[0, 50], [45, 50]]), [false, true],
                   "two labels that touch: the LAST never yields, so the first does");
  assert.deepEqual(lfTickKeep([[0, 50], [45, 50], [200, 50]]), [true, false, true],
                   "three: the later of the touching pair yields, because it is not the last tick");
  assert.deepEqual(lfTickKeep([]), []);
  assert.deepEqual(lfTickKeep([[0, 50]]), [true]);
});
