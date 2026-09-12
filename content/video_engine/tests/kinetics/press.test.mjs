// P50 T3 - THE PRESS CARD STACK (the push hand-off, doc 29 §9.27; Bravos shots 5-10). The whole pile's pose is a
// pure function of three numbers: which card, how many are live, and how far the newest is through its landing.
// These tests pin the newest's spring, the older cards' monotone slide back, the DIM per step, the transient that
// leaves nothing behind, n = 1 as the plain landing, and the underline's clock.
import { test } from "node:test";
import assert from "node:assert/strict";
import { minJerk } from "../../scripts/kinetics/ease.mjs";
import { springPop } from "../../scripts/kinetics/spring.mjs";
import { PRESS, pressRest, pressStack, underlineFrac, pressXf, pressPhraseBox,
         pressTypeScale, pressPictureFit, phoneCssPx,
         PRESS_FACES, pressFace, pressWords, pressWrap, pressPhraseFit, pressColumn,
         pressPhraseTarget, pressPhoneRead } from "../../scripts/species/press.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the dials are the stack's, and every clock and floor is a real one", () => {
  assert.ok(PRESS.LAND_S > 0 && PRESS.PUSH_S > 0 && PRESS.FADE_S > 0);
  assert.ok(PRESS.PUSH_S < PRESS.LAND_S, "the pile has taken the push before the newest stops overshooting");
  assert.ok(PRESS.POP_FROM > 0 && PRESS.POP_FROM < 1, "a card springs UP to its size, never from nothing");
  assert.ok(PRESS.BACK_SCALE > 0 && PRESS.BACK_SCALE < 1 && PRESS.DIM_MIN > 0 && PRESS.DIM_MIN < 1,
            "deep in the pile a card is smaller and dimmer, never gone");
  assert.ok(PRESS.STEP_PX > 0 && PRESS.STEP_SCALE > 0 && PRESS.DIM > 0);
  assert.ok(PRESS.SKEW_DEG > 0 && PRESS.SKEW_DEG < 8, "a lean, never a tumble");
});

// ------------------------------------------------------------------ the newest card (the badge spring)
test("the newest card's scale IS springPop: it overshoots by the POP preset and settles on its size", () => {
  let max = 0, maxAt = 0;
  for (let i = 0; i <= 60; i++) {
    const u = i / 60, pose = pressStack(2, 3, u);
    assert.equal(pose.depth, 0, "the last index is the newest");
    assert.ok(near(pose.scale, PRESS.POP_FROM + (1 - PRESS.POP_FROM) * springPop(u)), `u=${u}`);
    if (pose.scale > max) { max = pose.scale; maxAt = u; }
  }
  assert.ok(max > 1, "the landing overshoots - the card never lands twice");
  assert.ok(maxAt > 0 && maxAt < 1, `the overshoot is inside the clock (u=${maxAt})`);
  const rest = pressStack(2, 3, 1);
  assert.ok(near(rest.scale, 1, 1e-3) && near(rest.dy, 0, 1e-2), "it settles on its size, at its place");
  assert.deepEqual([rest.dx, rest.skew, rest.sx, rest.opacity], [0, 0, 1, 1], "the newest is lit, square and unmoved");
});

test("before its word the newest is above its place at POP_FROM, and not yet faded in", () => {
  const pose = pressStack(2, 3, 0);
  assert.equal(pose.scale, PRESS.POP_FROM);
  assert.equal(pose.dy, -PRESS.DROP_PX, "it waits a fixed drop above its place");
  assert.equal(pose.fade, 0);
  assert.equal(pressStack(2, 3, PRESS.FADE_S / PRESS.LAND_S).fade, 1, "the opacity ramp is FADE_S of wall clock");
});

// ------------------------------------------------------------------ the pile (the push hand-off)
test("the settled fan: each step behind is higher, smaller and dimmer, monotone, with both floors", () => {
  let prev = pressRest(0);
  assert.deepEqual([prev.dy, prev.scale, prev.opacity], [0, 1, 1], "the newest's rest pose is its own place");
  for (let d = 1; d <= 8; d++) {
    const r = pressRest(d);
    assert.ok(r.dy < prev.dy, `step ${d} sits higher than ${d - 1} - the masthead strips stay readable`);
    assert.ok(r.scale <= prev.scale && r.opacity <= prev.opacity, `step ${d} is no bigger and no brighter`);
    if (d <= 3) {
      assert.ok(near(r.scale, 1 - PRESS.STEP_SCALE * d), "STEP_SCALE per step, before the floor");
      assert.ok(near(r.opacity, 1 - PRESS.DIM * d), "DIM per step, before the floor");
    }
    prev = r;
  }
  assert.equal(pressRest(40).scale, PRESS.BACK_SCALE);
  assert.equal(pressRest(40).opacity, PRESS.DIM_MIN);
});

test("the push moves an older card from the pose it held to the pose of its new depth, and no further", () => {
  for (const [i, n] of [[0, 2], [1, 3], [0, 3], [2, 4]]) {
    const d = n - 1 - i, was = pressRest(d - 1), now = pressRest(d);
    const start = pressStack(i, n, 0), end = pressStack(i, n, 1);
    assert.equal(start.depth, d);
    assert.ok(near(start.dy, was.dy) && near(start.scale, was.scale) && near(start.opacity, was.opacity),
              `card ${i} of ${n} starts where it stood`);
    assert.ok(near(end.dy, now.dy) && near(end.scale, now.scale) && near(end.opacity, now.opacity),
              `card ${i} of ${n} ends at its new depth`);
    assert.ok(near(start.dx, 0) && near(end.dx, 0) && near(start.skew, 0) && near(end.skew, 0),
              "the shove is a transient: nothing of it survives either end");
    assert.ok(near(start.sx, 1) && near(end.sx, 1));
  }
});

test("the push's clock is minimum-jerk on PUSH_S, read off the newest's landing", () => {
  const i = 0, n = 2, was = pressRest(0), now = pressRest(1);
  for (let k = 0; k <= 20; k++) {
    const u = k / 20, p = minJerk(Math.min(1, u * PRESS.LAND_S / PRESS.PUSH_S));
    const pose = pressStack(i, n, u);
    assert.ok(near(pose.push, p), `u=${u}`);
    assert.ok(near(pose.dy, was.dy + (now.dy - was.dy) * p), "y on the push's clock");
    assert.ok(near(pose.opacity, was.opacity + (now.opacity - was.opacity) * p), "the dim on the same clock");
  }
  assert.equal(pressStack(i, n, 1).push, 1, "the push is complete before the landing is");
  assert.ok(pressStack(i, n, PRESS.PUSH_S / PRESS.LAND_S).push > 0.999);
});

test("x, scaleX and skewX are ONE pulse - the shove is the hand-off, not a wobble", () => {
  let peak = 0, peakAt = 0;
  for (let k = 0; k <= 60; k++) {
    const u = k / 60, pose = pressStack(0, 2, u);
    assert.ok(pose.dx <= 1e-12, "the pushed card is carried away from the newest, never toward it");
    assert.ok(pose.skew >= -1e-12 && pose.skew <= PRESS.SKEW_DEG + 1e-12);
    assert.ok(pose.sx <= 1 + 1e-12 && pose.sx >= 1 - PRESS.SQUEEZE - 1e-12, "scaleX only ever compresses");
    assert.ok(near(pose.skew / PRESS.SKEW_DEG, -pose.dx / PRESS.PUSH_DX, 1e-9), "one pulse drives all three");
    assert.ok(near(pose.skew / PRESS.SKEW_DEG, (1 - pose.sx) / PRESS.SQUEEZE, 1e-9));
    if (-pose.dx > peak) { peak = -pose.dx; peakAt = u; }
  }
  assert.ok(peak <= PRESS.PUSH_DX && peak > PRESS.PUSH_DX * 0.999, "the pulse reaches the full shove once, and never past it");
  assert.ok(peakAt > 0 && peakAt < PRESS.PUSH_S / PRESS.LAND_S, `the peak is inside the push (u=${peakAt})`);
});

test("n = 1 is the plain landing: one card, no pile, nothing pushed", () => {
  for (let k = 0; k <= 10; k++) {
    const u = k / 10, one = pressStack(0, 1, u), newest = pressStack(2, 3, u);
    assert.equal(one.depth, 0);
    assert.ok(near(one.scale, newest.scale) && near(one.dy, newest.dy));
    assert.deepEqual([one.dx, one.skew, one.sx, one.opacity], [0, 0, 1, 1]);
  }
});

test("the indices are clamped, so a stale index can never paint a card off the pile", () => {
  assert.equal(pressStack(9, 3, 0.5).depth, 0, "past the end is the newest");
  assert.equal(pressStack(-4, 3, 0.5).depth, 2, "before the start is the deepest");
  assert.equal(pressStack(0, 0, 0.5).depth, 0);
  for (const u of [-3, 0, 0.5, 1, 7]) for (const [i, n] of [[0, 3], [1, 3], [2, 3]]) {
    const p = pressStack(i, n, u);
    assert.ok(Number.isFinite(p.dx + p.dy + p.scale + p.sx + p.skew + p.opacity), `${i}/${n} @ ${u}`);
    assert.ok(p.opacity >= PRESS.DIM_MIN - 1e-12 && p.opacity <= 1 + 1e-12);
  }
});

// ------------------------------------------------------------------ the underline (E56's one exception)
test("the underline draws from nothing to the whole phrase, monotone, decelerating into the last letter", () => {
  assert.equal(underlineFrac(0), 0);
  assert.equal(underlineFrac(1), 1);
  assert.equal(underlineFrac(-1), 0);
  assert.equal(underlineFrac(4), 1);
  let prev = -1;
  for (let k = 0; k <= 40; k++) { const f = underlineFrac(k / 40); assert.ok(f > prev, `monotone at ${k / 40}`); prev = f; }
  assert.ok(underlineFrac(0.5) > 0.5, "the hand runs out fast and slows at the end");
  assert.ok(underlineFrac(0.9) > 0.99);
});

// ------------------------------------------------------------------ the geometry the underline rides
test("a box inside the card is carried through the card's own transform, about the pile's hinge", () => {
  const box = { x: 400, y: 200, w: 800, h: 400 };
  const still = pressXf(box, { scale: 1, sx: 1, skew: 0, dx: 0, dy: 0 });
  const q = { x: 500, y: 240, w: 300, h: 60 };
  const same = still(q);
  for (const k of ["x", "y", "w", "h"]) assert.ok(near(same[k], q[k], 1e-9), `an identity pose moves nothing (${k})`);
  const back = pressXf(box, pressRest(2))(q);
  assert.ok(back.w < q.w && back.h < q.h, "a card two steps back carries its phrase in smaller");
  assert.ok(back.y < q.y, "... and higher up the pile");
  const hinge = pressXf(box, { scale: 0.5, sx: 1, skew: 0, dx: 0, dy: 0 })({ x: box.x, y: box.y + box.h, w: box.w, h: 0 });
  assert.ok(near(hinge.y, box.y + box.h) && near(hinge.x + hinge.w / 2, box.x + box.w / 2),
            "the hinge is the card's bottom centre: the pile grows upward off one edge");
});

test("the phrase box is the card image's fractions, and a malformed one paints nothing", () => {
  const img = { x: 100, y: 50, w: 1000, h: 400 };
  const b = pressPhraseBox(img, { x0: 0.2, y0: 0.25, x1: 0.7, y1: 0.5 });
  [[b.x, 300], [b.y, 150], [b.w, 500], [b.h, 100]].forEach(([got, want]) => assert.ok(near(got, want, 1e-9)));
  assert.equal(pressPhraseBox(img, null), null);
  assert.equal(pressPhraseBox(null, { x0: 0, y0: 0, x1: 1, y1: 1 }), null);
  assert.equal(pressPhraseBox(img, { x0: 0, y0: 0, x1: "wide", y1: 1 }), null);
});

// ---- P50 T7 second watch: THE EMBEDDED CARD'S REFLOW ------------------------------------------------
// The card fills its surface, so the surface's box - not the card's - decides the layout. Two pure laws carry
// it: the type scales by ONE number, and the picture is fitted on ONE axis (fitting both is what a stretch is).

test("the type scale is the surface's width over the card's own, one number on both axes", () => {
  assert.ok(near(pressTypeScale(800, 800), 1), "a surface the card's own width changes nothing");
  assert.ok(near(pressTypeScale(794, 800), 0.9925), "the measured TV");
  assert.ok(near(pressTypeScale(1080, 800), 1.35), "a surface wider than the card scales its print UP");
  assert.ok(near(pressTypeScale(392, 800), 0.49), "... and the narrowest lawful surface scales it down");
  for (const bad of [0, -10, NaN]) assert.equal(pressTypeScale(bad, 800), 1, "a box with no width leaves the card alone");
  assert.equal(pressTypeScale(800, 0), 1, "a card with no authored width has nothing to scale from");
  // E62's own arithmetic, which is what a proof frame is read against: 48 px of a 1080-wide short is 17 CSS px
  assert.ok(near(phoneCssPx(48, 1080), 17, 1e-9));
  assert.ok(near(phoneCssPx(48 * 1920 / 1080, 1920), 17, 1e-9), "the same share of a landscape stage reads the same");
  assert.equal(phoneCssPx(100, 0), 0, "a stage with no width reads as nothing, rather than guessing one");
});

test("the picture keeps its own aspect: fitted on the width, or on the height, never on both", () => {
  const a = 160 / 528;
  const wide = pressPictureFit(752, 468, a);       // the TV: the width binds and the paper takes the rest
  assert.ok(near(wide.w, 752) && near(wide.h, a * 752, 1e-9));
  const tall = pressPictureFit(1000, 120, a);      // a short band: the height binds, so the picture narrows
  assert.ok(near(tall.h, 120) && near(tall.w, 120 / a, 1e-9));
  assert.ok(near(wide.h / wide.w, a, 1e-9) && near(tall.h / tall.w, a, 1e-9), "the aspect survives both branches");
  assert.equal(pressPictureFit(700, 400, 0), null, "no aspect on record: the caller leaves the picture's CSS alone");
  assert.equal(pressPictureFit(0, 400, a), null);
  assert.equal(pressPictureFit(700, -1, a), null);
});

// ---- R26-55: THE PULLED PHRASE AS LIVE TYPE -------------------------------------------------------
// A raster cannot re-line, so the words travel as data and the card SETS them. The laws under test: the wrap is
// greedy and never overruns the paper, the size is the largest that fits both axes (quantised, so one box gives
// one size), the column hands the picture its share and the words the rest, and the face is a dial with three
// candidates the operator picks from - never a new webfont.

// a monospace measurer: every character 0.6 em wide, which makes every expectation below arithmetic a reader can
// check by hand (the engine measures the real face; the LAW is what is under test here).
const CH = 0.6;
const w1of = (words) => words.map((w) => w.length * CH);
const PHRASE = "the historic normal has never once been normal";
const WORDS = pressWords(PHRASE);

test("the words are the operator's own, whitespace collapsed and nothing else touched", () => {
  assert.deepEqual(pressWords("  the historic \n normal  "), ["the", "historic", "normal"]);
  assert.deepEqual(pressWords(""), []);
  assert.deepEqual(pressWords(null), []);
  assert.deepEqual(pressWords(undefined), []);
  assert.equal(pressWords(PHRASE).join(" "), PHRASE, "the phrase survives the round trip word for word");
});

test("the wrap is greedy and no line is wider than the paper it was given", () => {
  const w1 = w1of(WORDS), size = 20, availW = 200;
  const lines = pressWrap(w1, CH, size, availW);
  assert.ok(lines.length > 1, "a phrase this long takes more than one line at 20 px");
  let seen = [];
  for (const l of lines) {
    assert.ok(l.w <= availW || l.words.length === 1, "only a word wider than the paper may overrun a line");
    seen = seen.concat(l.words);
  }
  assert.deepEqual(seen, WORDS.map((_w, i) => i), "every word is placed exactly once, in order");
  assert.equal(pressWrap(w1, CH, size, 100000).length, 1, "paper enough, one line");
  assert.equal(pressWrap([], CH, size, 200).length, 0, "no words, no lines");
});

test("the fit is the LARGEST size that fits both axes, quantised, one box giving one size", () => {
  const w1 = w1of(WORDS);
  const fit = pressPhraseFit(w1, CH, 500, 400);
  assert.ok(fit && fit.fits, "a phrase of eight words fits 500 x 400");
  assert.ok(fit.size > PRESS.TYPE_MIN && fit.size <= PRESS.TYPE_MAX);
  assert.ok(Math.abs(fit.size / PRESS.TYPE_Q - Math.round(fit.size / PRESS.TYPE_Q)) < 1e-9, "quantised to TYPE_Q");
  assert.ok(near(fit.h, fit.lines.length * fit.size * PRESS.LINE_H, 1e-9) && fit.h <= 400);
  assert.deepEqual(pressPhraseFit(w1, CH, 500, 400), fit, "the same box gives the same size and lines, always");
  const up = pressPhraseFit(w1, CH, 500, 400 + fit.size * PRESS.LINE_H * 2);
  assert.ok(up.size > fit.size, "more paper, bigger type - which is the whole point of live type on a tall poster");
  assert.ok(pressPhraseFit(w1, CH, 200, 60).size < fit.size, "less paper, smaller type");
  assert.equal(pressPhraseFit(w1, CH, 100000, 100000).size, PRESS.TYPE_MAX, "the ceiling holds: a headline, not a title card");
});

test("a box that cannot hold the phrase at the floor says so, and never drops a word", () => {
  const w1 = w1of(WORDS);
  const tiny = pressPhraseFit(w1, CH, 40, 20);
  assert.equal(tiny.fits, false, "the build is told, rather than the card hiding it");
  assert.equal(tiny.size, PRESS.TYPE_MIN);
  assert.equal(tiny.lines.reduce((n, l) => n + l.words.length, 0), WORDS.length, "every word is still on the card");
  assert.equal(pressPhraseFit([], CH, 500, 400), null, "no words, no fit");
  assert.equal(pressPhraseFit(w1, CH, 0, 400), null);
  assert.equal(pressPhraseFit(w1, CH, 500, 0), null);
});

test("every line the fit returns fits the paper in the DOM too - the air is what keeps it there", () => {
  const w1 = w1of(WORDS);
  for (const [availW, availH] of [[500, 400], [900, 300], [300, 900], [551, 850]]) {
    const fit = pressPhraseFit(w1, CH, availW, availH);
    for (const l of fit.lines) assert.ok(l.w <= availW * (1 - PRESS.WORD_AIR) + 1e-9,
      availW + "x" + availH + ": a measured line is inside the paper, with the air still clear");
  }
});

test("the column hands the picture its share of the paper and the words the rest", () => {
  const a = 160 / 528, paper = 800, w = 500;
  const col = pressColumn(paper, w, a);
  assert.ok(col.prov && near(col.prov.h / col.prov.w, a, 1e-9), "the strip keeps the crop's own aspect");
  assert.ok(col.provH <= paper * PRESS.PROV_SHARE + 1e-9, "the strip never takes more than its share");
  assert.ok(near(col.phraseH, paper - col.provH - col.gap, 1e-9), "the words take everything left");
  assert.ok(col.phraseH > col.provH, "the phrase is the hero; the raster is the citation");
  const tall = pressColumn(paper, w, 4);            // a tall crop: the share binds and the strip narrows
  assert.ok(near(tall.provH, paper * PRESS.PROV_SHARE, 1e-9) && tall.prov.w < w);
  assert.equal(pressColumn(0, w, a), null);
  assert.equal(pressColumn(paper, 0, a), null);
  const noAspect = pressColumn(paper, w, 0);
  assert.equal(noAspect.prov, null, "no aspect on record: the caller leaves the picture's CSS alone");
  assert.ok(near(noAspect.provH, paper * PRESS.PROV_SHARE, 1e-9));
});

test("the underline rides the LIVE type when there is any, and the crop's own box when there is not", () => {
  const img = { x: 100, y: 50, w: 1000, h: 400 }, frac = { x0: 0.2, y0: 0.25, x1: 0.7, y1: 0.5 };
  const live = { x: 120, y: 80, w: 700, h: 220 };
  assert.deepEqual(pressPhraseTarget(live, img, frac), live, "the words moved, so the mark moves with them");
  assert.deepEqual(pressPhraseTarget(null, img, frac), pressPhraseBox(img, frac), "no live type: the crop's region");
  assert.deepEqual(pressPhraseTarget({ x: 0, y: 0, w: 0, h: 0 }, img, frac), pressPhraseBox(img, frac),
                   "a phrase element with no box yet is no target - an underline is never drawn on nothing");
  assert.equal(pressPhraseTarget(null, null, frac), null);
});

test("the phone reading is reported against E62's floor and never clamped to it", () => {
  const under = pressPhoneRead(38, 1080);       // about what the raster reads at on the measured poster
  assert.equal(under.floor, PRESS.PHONE_FLOOR);
  assert.equal(under.clears, false, "13-14 CSS px on a phone is the defect R26-55 exists for");
  const over = pressPhoneRead(100, 1080);
  assert.ok(over.clears && over.css > PRESS.PHONE_FLOOR, "live type on a tall surface clears the floor by a mile");
  assert.ok(near(pressPhoneRead(48, 1080).css, 17, 1e-9), "E62's own arithmetic, to the digit");
  assert.equal(pressPhoneRead(48, 0).css, 0);
});

test("the three faces are the operator's to choose, and not one of them downloads a thing", () => {
  assert.deepEqual(Object.keys(PRESS_FACES), ["house", "serif", "condensed"]);
  assert.equal(PRESS.FACE, "house", "the default is the house face until the operator rules (gate 7)");
  assert.equal(pressFace(undefined).id, "house");
  assert.equal(pressFace("SERIF").id, "serif", "the dial is read case-insensitively");
  assert.equal(pressFace("no-such-face").id, "house", "a typo can never blank a card");
  const fams = new Set();
  for (const [id, f] of Object.entries(PRESS_FACES)) {
    assert.equal(f.id, id);
    assert.ok(f.weight >= 400 && f.weight <= 900 && typeof f.track === "string");
    assert.ok(f.label.length > 20, id + " says what it is, so a choice off a frame is a choice with a name");
    assert.ok(/(sans-serif|serif)$/.test(f.family), id + " ends in a generic family - a face is never assumed present");
    assert.ok(!/Kalam/.test(f.family), "the ledger's hand is not a masthead");
    fams.add(f.family);
  }
  assert.equal(fams.size, 3, "three candidates, three different stacks");
});
