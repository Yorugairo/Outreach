// P71 T14 (was P69 T55; RESCOPED by BOOM's frames, VERIFY.md row T32) - THE DECADE RULER: a scrolling time-passage
// GROUND. A full-width ruler (a tick a year, a taller one each five, the tallest each decade under a large faded numeral)
// enters at the stage's right edge, scrolls left on a decelerating ease and LANDS with its settle decades framed, then
// holds. It pins nothing: the chips a recipe lays above it are their own species. These tests pin the law (true years at
// even spacing, the settle exact, the scroll a pure function of t that travels one way), the numerals (every decade in
// the strip, alternating below / above as the witness frames alternate them), the leave, and the painter through ctx.
import { test } from "node:test";
import assert from "node:assert/strict";
import { RULER, rulerScale, rulerRest, rulerScroll, rulerOrigin, rulerYearX, rulerTicks, rulerNumerals, rulerFade,
         rulerPose, rulerY, rulerBandHalf, rulerGroundSamples, rulerInk, paintRuler } from "../../scripts/species/ruler.mjs";

const W = 1920, H = 1080;
const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const R = (o = {}) => Object.assign({ kind: "ruler", at: 50.5, dur: 10.0, from: 1980, to: 2030, settle: [2000, 2010, 2020] }, o);

test("the dials: the witness's scroll, its framing, its line, and a ground that is faint beside its ticks", () => {
  assert.ok(RULER.SCROLL_S >= 1.0 && RULER.SCROLL_S <= 2.0, "BOOM 05:50.5 -> 05:52.0: the strip lands in ~1.5 s");
  assert.equal(RULER.LEAD, 2.0, "hermite(0, 1, LEAD, 0) with LEAD 2 is the ease-out quad 2u - u^2 (lands at rest)");
  assert.ok(RULER.SETTLE_L > 0 && RULER.SETTLE_L < RULER.SETTLE_R && RULER.SETTLE_R < 1);
  assert.ok(RULER.Y > 0.5 && RULER.Y < 0.8, "the ruler sits BELOW the middle, leaving the room above it for the chip row");
  assert.ok(RULER.Y_PORTRAIT > 0.5 && RULER.Y_PORTRAIT < RULER.Y, "9:16: above the short's caption home, still below the middle");
  assert.ok(RULER.TICK_DECADE_H > RULER.TICK_HALF_H && RULER.TICK_HALF_H > RULER.TICK_YEAR_H && RULER.TICK_YEAR_H > RULER.TICK_SUB_H);
  assert.ok(RULER.NUM_ALPHA < 0.3 && RULER.NUM_ALPHA < RULER.TICK_SUB_ALPHA, "the numerals are the faded ground, never the subject");
  assert.ok(RULER.NUM_SIZE >= 59.08, "every label at least the s90 floor (ledger_page.CARD_TYPE_PX)");
  assert.ok(RULER.SUB >= 1 && Number.isInteger(RULER.SUB));
  assert.equal(RULER.SETTLE_MIN, 2);
  assert.equal(RULER.SETTLE_MAX, 4);
});

test("the scroll ease: from rest-less entry to a landing at rest, monotone, clamped, 0 and 1 exactly at the ends", () => {
  assert.equal(rulerScroll(0), 0);
  assert.equal(rulerScroll(1), 1);
  assert.equal(rulerScroll(-3), 0);
  assert.equal(rulerScroll(7), 1);
  for (let i = 0; i <= 40; i++) assert.ok(near(rulerScroll(i / 40), 2 * (i / 40) - (i / 40) ** 2, 1e-12), "the ease-out quad");
  let prev = -1;
  for (let i = 0; i <= 100; i++) { const p = rulerScroll(i / 100); assert.ok(p >= prev); prev = p; }
  assert.ok(rulerScroll(1 / 3) > 0.5, "front-loaded: past half the travel at a third of the time (BOOM: 51 %)");
});

test("true years at even spacing: one scale for the whole strip, the settle decades landing exactly on their marks", () => {
  const sp = R(), ppy = rulerScale(sp, W);
  assert.ok(near(ppy, (RULER.SETTLE_R - RULER.SETTLE_L) * W / 20));
  const o = rulerRest(sp, W);
  assert.ok(near(rulerYearX(o, ppy, sp.from, 2000), RULER.SETTLE_L * W, 1e-9), "the first settle decade at SETTLE_L");
  assert.ok(near(rulerYearX(o, ppy, sp.from, 2020), RULER.SETTLE_R * W, 1e-9), "the last at SETTLE_R");
  assert.ok(near(rulerYearX(o, ppy, sp.from, 2010), (RULER.SETTLE_L + RULER.SETTLE_R) / 2 * W, 1e-9));
  for (let y = 1980; y < 2030; y++)
    assert.ok(near(rulerYearX(o, ppy, sp.from, y + 1) - rulerYearX(o, ppy, sp.from, y), ppy, 1e-9), "even per year");
  const two = R({ settle: [2000, 2010] });
  assert.ok(near(rulerScale(two, W), 2 * ppy), "two decades framed over the same width: twice the px per year");
});

test("a portrait stage frames the window tighter, so the outer numerals stay on it - the same law, another pair", () => {
  const sp = R(), PW = 1080, PH = 1920;
  const o = rulerRest(sp, PW, PH), ppy = rulerScale(sp, PW, PH);
  assert.ok(near(rulerYearX(o, ppy, sp.from, 2000), RULER.SETTLE_L_PORTRAIT * PW, 1e-9));
  assert.ok(near(rulerYearX(o, ppy, sp.from, 2020), RULER.SETTLE_R_PORTRAIT * PW, 1e-9));
  const half = 2.62 * RULER.NUM_SIZE / 2;   /* a four-digit numeral's half-width, Inter 800 [DERIVED: the portrait probe] */
  assert.ok(RULER.SETTLE_L_PORTRAIT * PW - half > 0 && RULER.SETTLE_R_PORTRAIT * PW + half < PW, "both outer numerals on stage");
  assert.ok(near(rulerPose(sp, sp.at + 3, PW, PH).origin, o), "the pose reads the stage's own aspect");
  assert.ok(near(rulerScale(sp, W), rulerScale(sp, W, H)), "landscape: the H-less call is the landscape call");
});

test("the entry: at its word the strip's first year stands at the stage's right edge - the ruler wipes on from there", () => {
  const sp = R();
  assert.equal(rulerOrigin(sp, sp.at, W), W);
  assert.equal(rulerOrigin(sp, sp.at - 1, W), W, "before its word nothing has moved");
  assert.ok(near(rulerOrigin(sp, sp.at + RULER.SCROLL_S, W), rulerRest(sp, W), 1e-9), "landed at SCROLL_S");
  assert.ok(near(rulerOrigin(sp, sp.at + RULER.SCROLL_S + 5, W), rulerRest(sp, W), 1e-9), "... and HOLDS (the ground)");
  let prev = Infinity;
  for (let i = 0; i <= 60; i++) {
    const x = rulerOrigin(sp, sp.at + RULER.SCROLL_S * i / 60, W);
    assert.ok(x <= prev + 1e-9, "one way only: time passes to the right-to-left, never back");
    prev = x;
  }
});

test("seek-exact: the pose is a pure function of t - the same t from any order is the same pose", () => {
  const sp = R();
  const ts = [51.2, 50.6, 55.0, 51.2, 60.4, 50.6];
  const poses = ts.map((t) => JSON.stringify(rulerPose(sp, t, W, H)));
  assert.equal(poses[0], poses[3]);
  assert.equal(poses[1], poses[5]);
});

test("the ticks: a tick a year, SUB between, a taller one each five and the tallest each decade - and none outside from..to", () => {
  const sp = R(), ppy = rulerScale(sp, W), o = rulerRest(sp, W);
  const ticks = rulerTicks(sp, o, ppy, W);
  const years = ticks.filter((k) => k.level !== "sub");
  for (const k of ticks) assert.ok(k.year >= sp.from - 1e-9 && k.year <= sp.to + 1e-9, "inside the strip");
  for (const k of ticks) assert.ok(k.x >= -RULER.PAD_PX && k.x <= W + RULER.PAD_PX, "only what the stage can show");
  for (const k of years) {
    assert.ok(Number.isInteger(k.year));
    const want = k.year % 10 === 0 ? "decade" : k.year % 5 === 0 ? "half" : "year";
    assert.equal(k.level, want, "year " + k.year);
    assert.ok(near(k.x, rulerYearX(o, ppy, sp.from, k.year), 1e-9), "each tick stands on its own year");
  }
  const d2010 = ticks.find((k) => k.year === 2010);
  assert.equal(d2010.level, "decade");
  const subs = ticks.filter((k) => k.level === "sub" && k.year > 2010 && k.year < 2011);
  assert.equal(subs.length, RULER.SUB - 1, "SUB - 1 marks between two years");
  assert.ok(!ticks.some((k) => k.level === "sub" && k.year > sp.to), "the strip ends at `to`");
});

test("the numerals: every decade the strip holds, its own year's text, even decades below, odd above", () => {
  const sp = R(), ppy = rulerScale(sp, W);
  const at51 = rulerNumerals(sp, rulerOrigin(sp, sp.at + 0.5, W), ppy, W);
  const rest = rulerNumerals(sp, rulerRest(sp, W), ppy, W);
  assert.deepEqual(rest.map((n) => n.text), ["2000", "2010", "2020"], "the settled window reads 2000 / 2010 / 2020");
  assert.deepEqual(rest.map((n) => n.side), ["below", "above", "below"], "the witness: 2000 below, 2010 above, 2020 below");
  assert.ok(at51.some((n) => n.text === "1980" && n.side === "below") || at51.some((n) => n.text === "1990" && n.side === "above"),
            "mid-scroll the earlier decades pass (BOOM 05:51.0: 1980 below, 1990 above)");
  const o = rulerRest(sp, W);
  for (const n of rest) assert.ok(near(n.x, rulerYearX(o, ppy, sp.from, n.year), 1e-9), "centred on its decade tick");
  const all = rulerNumerals(R({ from: 1983, to: 2027 }), rulerRest(R({ from: 1983, to: 2027 }), W), ppy, W * 50);
  assert.ok(all.every((n) => n.year >= 1983 && n.year <= 2027 && n.year % 10 === 0), "no numeral outside the strip");
});

test("the leave: whole through the hold, gone at the end of dur over OUT_S; nothing before its word", () => {
  const sp = R();
  assert.equal(rulerFade(sp, sp.at - 0.01), 0);
  assert.equal(rulerFade(sp, sp.at), 1);
  assert.ok(near(rulerFade(sp, sp.at + sp.dur - RULER.OUT_S), 1, 1e-9), "whole at the leave's first instant (float sums)");
  assert.equal(rulerFade(sp, sp.at + sp.dur), 0);
  const mid = rulerFade(sp, sp.at + sp.dur - RULER.OUT_S / 2);
  assert.ok(mid > 0 && mid < 1);
});

test("the pose carries the line, the scale and the offset; an authored y moves the line and nothing else", () => {
  const sp = R();
  const p = rulerPose(sp, sp.at + 3, W, H);
  assert.ok(near(p.y, RULER.Y * H));
  assert.ok(near(p.ppy, rulerScale(sp, W)));
  assert.ok(near(p.origin, rulerRest(sp, W)));
  assert.ok(near(rulerPose(sp, sp.at + 3, 1080, 1920).y, RULER.Y_PORTRAIT * 1920), "a portrait stage takes its own default line");
  const q = rulerPose(R({ y: 0.7 }), sp.at + 3, W, H);
  assert.ok(near(q.y, 0.7 * H));
  assert.equal(q.origin, p.origin);
});

// ---------------------------------------------------------------- the painter, through ctx only
const fakeEl = () => {
  const made = [];
  const el = (tag, cls, parent, attrs = {}) => { const n = { tag, cls, parent, attrs, children: [], textContent: "" }; made.push(n); if (parent && parent.children) parent.children.push(n); return n; };
  return { el, made };
};

test("paintRuler draws one group: four tick paths and the numerals, faded by its leave, offset by its idle", () => {
  const { el, made } = fakeEl();
  const svg = { children: [] };
  const sp = R({ idle: "drift" });
  let idleAsked = null;
  const idle = (kind, t, phase) => { idleAsked = kind; return { scale: 1, dx: 3, dy: -2, lum: 1 }; };
  paintRuler({ sp, t: sp.at + 4, svg, el, idle, hash: () => 0.25, seed: 1, si: 0, STAGE_W: W, STAGE_H: H });
  assert.equal(idleAsked, "drift", "the named idle is the engine's (the life clock's), never a clock of its own");
  const g = made.find((n) => n.tag === "g");
  assert.ok(g && g.parent === svg);
  assert.match(g.attrs.transform, /^translate\(3\.00 -2\.00\)$/);
  const paths = made.filter((n) => n.tag === "path");
  assert.equal(paths.length, 4, "decade / half / year / sub");
  for (const p of paths) assert.ok(p.attrs.d.startsWith("M"), "each level one path");
  const texts = made.filter((n) => n.tag === "text").map((n) => n.textContent);
  assert.deepEqual(texts, ["2000", "2010", "2020"]);
  assert.ok(!made.some((n) => n.tag === "circle" || n.tag === "rect"), "no pin, no card, no marker: a ground");
});

test("paintRuler paints nothing before its word and nothing once it has left", () => {
  for (const t of [40, 60.5, 70]) {
    const { el, made } = fakeEl();
    paintRuler({ sp: R(), t, svg: { children: [] }, el, idle: () => ({ scale: 1, dx: 0, dy: 0 }), hash: () => 0, seed: 0, si: 0,
                 STAGE_W: W, STAGE_H: H });
    assert.equal(made.length, 0, "t " + t);
  }
});

test("without an idle the ground is still: no idle is asked for and the group carries no transform", () => {
  const { el, made } = fakeEl();
  let asked = false;
  paintRuler({ sp: R(), t: 55, svg: { children: [] }, el, idle: () => { asked = true; return { scale: 1, dx: 5, dy: 5 }; },
               hash: () => 0, seed: 0, si: 0, STAGE_W: W, STAGE_H: H });
  assert.equal(asked, false);
  assert.equal(made.find((n) => n.tag === "g").attrs.transform, undefined);
});

// ---------------------------------------------------------------- the line per aspect, the band, the ink by its ground
test("the default line is the aspect's, clear of the stage caption's home strip; an authored y wins", () => {
  assert.equal(rulerY(R(), W, H), RULER.Y);
  assert.equal(rulerY(R(), 1080, 1920), RULER.Y_PORTRAIT);
  assert.equal(rulerY(R({ y: 0.3 }), 1080, 1920), 0.3);
  const half = rulerBandHalf();
  assert.ok(near(half, RULER.TICK_DECADE_H / 2 + RULER.NUM_GAP + RULER.NUM_CAP * RULER.NUM_SIZE));
  /* the compiler's caption_home_box: 16:9 y 432 h 143, 9:16 y 1297 h 143 (8 px of air, NEWSREEL_STRIP_PAD) */
  assert.ok(RULER.Y * 1080 - half >= 432 + 143 + 8, "16:9: the band starts below the caption's strip");
  assert.ok(RULER.Y * 1080 + half <= 1080, "... and ends on the stage");
  assert.ok(RULER.Y_PORTRAIT * 1920 + half <= 1297 - 8, "9:16: the band ends above the caption's strip");
});

test("the ground is read across the width, on the line and at the band's two edges", () => {
  const pts = rulerGroundSamples(700, W);
  assert.equal(pts.length, 3 * RULER.GROUND_SAMPLES);
  const ys = [...new Set(pts.map((p) => p[1]))].sort((a, b) => a - b);
  assert.deepEqual(ys, [700 - rulerBandHalf(), 700, 700 + rulerBandHalf()]);
  assert.ok(pts.every((p) => p[0] > 0 && p[0] < W));
});

test("the ink: chalk on a dark ground or none measured, charcoal on a light one", () => {
  const lum = (r, g, b) => [r, g, b].map((v) => v / 255).map((c) => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)))
    .reduce((a, c, i) => a + c * [0.2126, 0.7152, 0.0722][i], 0);
  assert.equal(rulerInk(null), RULER.INK);
  assert.equal(rulerInk(undefined), RULER.INK);
  assert.equal(rulerInk(lum(43, 52, 60)), RULER.INK, "the golden's dark plate");
  assert.equal(rulerInk(lum(37, 49, 60)), RULER.INK, "the ledger's charcoal field");
  assert.equal(rulerInk(lum(244, 230, 199)), RULER.INK_DARK, "a cream plate or page");
  assert.equal(rulerInk(lum(255, 255, 255)), RULER.INK_DARK);
});

test("paintRuler inks its ticks and numerals by the ground ctx.groundLum measures under its band", () => {
  const { el, made } = fakeEl();
  let asked = null;
  const groundLum = (pts) => { asked = pts; return 0.8; };   /* a cream ground */
  paintRuler({ sp: R(), t: 55, svg: { children: [] }, el, idle: () => ({ scale: 1, dx: 0, dy: 0 }), hash: () => 0, seed: 0, si: 0,
               STAGE_W: W, STAGE_H: H, groundLum });
  assert.equal(asked.length, 3 * RULER.GROUND_SAMPLES, "it asks at its own samples");
  assert.ok(made.filter((n) => n.tag === "path").every((n) => n.attrs.stroke === RULER.INK_DARK));
  assert.ok(made.filter((n) => n.tag === "text").every((n) => n.attrs.style.includes("fill: " + RULER.INK_DARK)));
});
