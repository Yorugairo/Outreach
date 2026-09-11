// P50 T2 - THE ICON CHIP (the Bravos icon board, shots 26-28). The chip's whole visual state is a pure function of
// t, sp.at and sp.cross_at: the badge spring lands it, the two-stroke X crosses it on a LATER word, and the card
// dims to DIM as that X completes. These tests pin the three, and pin that nothing is remembered between calls.
import { test } from "node:test";
import assert from "node:assert/strict";
import { SPRING, springPop } from "../../scripts/kinetics/spring.mjs";
import { CHIP, chipLand, chipCrossF, chipStrokes, chipPose, chipGeometry, paintChip } from "../../scripts/species/chip.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const chip = (o = {}) => Object.assign({ kind: "chip", at: 4, dur: 6, icon: "factory", label: "STEEL" }, o);

test("the dials are the chip's, and every clock is a real window", () => {
  assert.ok(CHIP.LAND_S > 0 && CHIP.CROSS_S > 0 && CHIP.FADE_S > 0);
  assert.ok(CHIP.POP_FROM > 0 && CHIP.POP_FROM < 1, "a chip springs UP to its size, never from nothing");
  assert.ok(CHIP.DIM > 0 && CHIP.DIM < 1, "a crossed chip dims but stays legible - it is still one of the set");
  assert.equal(CHIP.DIM, 0.55);
  assert.ok(CHIP.GLYPH < CHIP.SIZE, "the glyph sits inside the card");
});

// ---------------------------------------------------------------- the landing (the badge spring)
test("the landing IS springPop: the scale at k is POP_FROM + (1 - POP_FROM) * springPop(k)", () => {
  const sp = chip();
  for (let i = 0; i < 40; i++) {   // the closed end is the float-exact case below: (at + LAND_S) - at is not LAND_S to the bit
    const k = i / 40, t = sp.at + k * CHIP.LAND_S;
    assert.ok(near(chipLand(t, sp.at).scale, CHIP.POP_FROM + (1 - CHIP.POP_FROM) * springPop(k)), `k=${k}`);
    assert.ok(near(chipPose(sp, t).scale, chipLand(t, sp.at).scale), "the pose reads the same landing");
  }
  assert.ok(near(chipLand(sp.at + CHIP.LAND_S, sp.at).scale, 1, 1e-3), "the settle lands on its size");
});

test("before its word nothing has landed; after LAND_S it is exactly at rest", () => {
  const sp = chip();
  const before = chipLand(sp.at - 1, sp.at);
  assert.equal(before.u, 0);
  assert.equal(before.scale, CHIP.POP_FROM);
  assert.equal(before.fade, 0);
  assert.equal(before.dy, -CHIP.DROP_PX, "it waits a fixed drop above its place");
  for (const t of [sp.at + CHIP.LAND_S, sp.at + CHIP.LAND_S + 3]) {
    const on = chipLand(t, sp.at);
    assert.ok(near(on.scale, 1, 1e-3));
    assert.ok(near(on.dy, 0, 0.05), "under a tenth of a px: the painter writes the drop to one decimal");
    assert.equal(on.fade, 1);
  }
  const rest = chipLand(sp.at + CHIP.LAND_S * 2, sp.at);   // past the clock the spring is clamped: exactly at rest, to the bit
  assert.deepEqual([rest.u, rest.scale, rest.dy, rest.fade], [1, 1, 0, 1]);
});

test("R26-20's landing overshoots by the POP preset and settles - the card never lands twice", () => {
  const sp = chip();
  let max = 0, maxAt = 0;
  for (let i = 0; i <= 2000; i++) {
    const k = i / 2000, s = chipLand(sp.at + k * CHIP.LAND_S, sp.at).scale;
    if (s > max) { max = s; maxAt = k; }
  }
  assert.ok(near(max, 1 + (1 - CHIP.POP_FROM) * SPRING.MP, 1e-4), `peak ${max}`);
  assert.ok(maxAt > 0.3 && maxAt < 0.9, "the overshoot is inside the clock, not at its end");
  let crossings = 0, prev = chipLand(sp.at, sp.at).scale;
  for (let i = 1; i <= 2000; i++) {
    const s = chipLand(sp.at + (i / 2000) * CHIP.LAND_S, sp.at).scale;
    if ((prev < 1) !== (s < 1)) crossings++;
    prev = s;
  }
  assert.ok(crossings <= 2, `one overshoot and one settle, not a bounce: ${crossings} crossings`);
});

// ---------------------------------------------------------------- the cross (the retraction)
test("the cross is 0 until cross_at, half at half CROSS_S, 1 after - and only ever forward", () => {
  const sp = chip({ cross_at: 9 });
  assert.equal(chipCrossF(sp, 8.9), 0);
  assert.equal(chipCrossF(sp, sp.cross_at), 0);
  assert.ok(near(chipCrossF(sp, sp.cross_at + CHIP.CROSS_S / 2), 0.5));
  assert.equal(chipCrossF(sp, sp.cross_at + CHIP.CROSS_S), 1);
  assert.equal(chipCrossF(sp, sp.cross_at + 40), 1);
  let prev = -1;
  for (let i = 0; i <= 500; i++) { const f = chipCrossF(sp, i / 10); assert.ok(f >= prev); prev = f; }
});

test("a chip with no cross_at is never crossed, unless it was DECLARED crossed", () => {
  assert.equal(chipCrossF(chip(), 99), 0);
  assert.equal(chipCrossF(chip({ state: "on" }), 99), 0);
  assert.equal(chipCrossF(chip({ state: "crossed" }), 0), 1, "a board read back after the fact lands crossed");
  assert.equal(chipCrossF(chip({ state: "crossed" }), 99), 1);
});

test("the X is two strokes: the first over the cross's first half, the second over its second", () => {
  assert.deepEqual(chipStrokes(0), [0, 0]);
  assert.deepEqual(chipStrokes(0.25), [0.5, 0]);
  assert.deepEqual(chipStrokes(0.5), [1, 0]);
  assert.deepEqual(chipStrokes(0.75), [1, 0.5]);
  assert.deepEqual(chipStrokes(1), [1, 1]);
});

test("the card dims to DIM as the X completes, and not before its word", () => {
  const sp = chip({ cross_at: 9 });
  assert.equal(chipPose(sp, 8.9).dim, 1);
  assert.ok(near(chipPose(sp, sp.cross_at + CHIP.CROSS_S / 2).dim, 1 - (1 - CHIP.DIM) / 2));
  assert.ok(near(chipPose(sp, sp.cross_at + CHIP.CROSS_S).dim, CHIP.DIM));
  assert.ok(near(chipPose(sp, sp.cross_at + 30).dim, CHIP.DIM));
  assert.equal(chipPose(chip(), 99).dim, 1, "an uncrossed chip never dims");
});

// ---------------------------------------------------------------- pure function of t
test("a seek IS the play: the same t gives the same bits, in any order, with nothing remembered", () => {
  const sp = chip({ cross_at: 9, idle: "breath" });
  const forward = [], backward = [];
  for (let i = 0; i <= 300; i++) forward.push(JSON.stringify(chipPose(sp, i / 20)));
  for (let i = 300; i >= 0; i--) backward.unshift(JSON.stringify(chipPose(sp, i / 20)));
  assert.deepEqual(backward, forward);
  assert.equal(JSON.stringify(chipPose(sp, 7.35)), forward[147]);
});

test("nothing in the module reaches for a clock or a random", () => {
  const src = paintChip.toString() + chipPose.toString() + chipLand.toString() + chipCrossF.toString();
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});

// ---------------------------------------------------------------- the sourced glyph
test("the glyph comes from the asset map's geometry, and garbage is refused rather than drawn", () => {
  const good = JSON.stringify({ vb: [0, 0, 24, 24], el: [{ t: "path", a: { d: "M12 16h.01" } }] });
  assert.deepEqual(chipGeometry(good).el, [{ t: "path", a: { d: "M12 16h.01" } }]);
  for (const bad of [null, undefined, "", "not json", "{}", JSON.stringify({ vb: [0, 0, 24, 24], el: [] }), 7])
    assert.equal(chipGeometry(bad), null, String(bad));
});

// ---------------------------------------------------------------- the painter, on a stub surface
test("the painter draws nothing when the target does not resolve, and one group when it does", () => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [], textContent: "", setAttribute(k, v) { this.at[k] = v; }, getAttribute(k) { return this.at[k]; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  const ctx = (target, t) => ({
    sp: chip({ target, cross_at: 9 }), t, svg: { kids: [] }, el, A: { "icon:factory": JSON.stringify({ vb: [0, 0, 24, 24], el: [{ t: "path", a: { d: "M12 16h.01" } }] }) },
    resolveTarget: (tg) => (tg ? { x: 100, y: 200, w: 0, h: 0 } : null),
    drawOn: (p, k) => p.setAttribute("stroke-dashoffset", k.toFixed(3)), hash: () => 0.5,
    idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0,
  });
  paintChip(ctx(null, 5));
  assert.equal(made.length, 0, "the targeting law: no resolved target, nothing painted");
  paintChip(ctx({ kind: "point", x: 0.5, y: 0.5 }, 5));
  const tags = made.map((e) => e.tag);
  assert.deepEqual(tags, ["g", "g", "rect", "g", "path", "text"], tags);
  assert.equal(made.find((e) => e.cls === "chiplab").textContent, "STEEL");
  made.length = 0;
  paintChip(ctx({ kind: "point", x: 0.5, y: 0.5 }, 9.4));   // mid-cross: the first stroke is in, the second drawing
  const xs = made.filter((e) => e.cls === "sq");
  assert.equal(xs.length, 2, "the two-stroke X");
  assert.equal(xs[0].at["stroke-dashoffset"], "1.000");
  assert.ok(+xs[1].at["stroke-dashoffset"] > 0 && +xs[1].at["stroke-dashoffset"] < 1);
});
