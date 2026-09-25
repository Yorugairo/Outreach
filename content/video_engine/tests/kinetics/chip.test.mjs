// P50 T2 - THE ICON CHIP (the Bravos icon board, shots 26-28). The chip's whole visual state is a pure function of
// t, sp.at and sp.cross_at: the badge spring lands it, the two-stroke X crosses it on a LATER word, and the card
// dims to DIM as that X completes. These tests pin the three, and pin that nothing is remembered between calls.
import { test } from "node:test";
import assert from "node:assert/strict";
import { SPRING, springPop } from "../../scripts/kinetics/spring.mjs";
import { CHIP, CHIP_STAMP, chipLand, chipCrossF, chipStrokes, chipPose, chipGeometry, chipStampLabelLines, paintChip } from "../../scripts/species/chip.mjs";

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

test("the opt-in stamp uses an approved raster prop, spring landing and no generic card", () => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [], textContent: "", setAttribute(k, v) { this.at[k] = v; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  const sp = { kind: "chip", form: "stamp", at: 4, dur: 6, size: 260,
    icon: "prop-badge-dram-memory-etf-v1", _catalogue: "icons", label: "DRAM\nETF", ink: "charcoal", target: { kind: "point", x: .5, y: .5 } };
  paintChip({ sp, t: 4.2, svg: { kids: [] }, el,
    A: { "prop:prop-badge-dram-memory-etf-v1": "data:image/png;base64,approved" },
    resolveTarget: () => ({ x: 960, y: 540, w: 0, h: 0 }), hash: () => .5,
    idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 });
  assert.deepEqual(made.map((e) => e.tag), ["g", "image", "text", "tspan", "tspan"]);
  assert.equal(made[1].cls, "chipstampart");
  assert.equal(made[1].at.href, "data:image/png;base64,approved");
  assert.equal(made[1].at.preserveAspectRatio, "xMidYMid meet");
  assert.equal(made[1].at.width, String(CHIP_STAMP.SIZE.toFixed(1)));
  assert.match(made[2].at.style, /font-family:Kalam/);
  assert.match(made[2].at.style, /font-size:48px/);
  assert.match(made[2].at.style, /fill:#25313C/);
  assert.match(made[2].at.style, /paint-order:stroke;stroke:#F4E6C7;stroke-width:4px/,
    "printed labels need a narrow contrast keyline over narrative artwork");
  assert.deepEqual(made.slice(3).map((e) => e.textContent), ["DRAM", "ETF"]);
  assert.deepEqual(chipStampLabelLines("A\nB\nC"), ["A", "B", "C"]);
  assert.ok(!made.some((e) => e.tag === "rect"), "stamp has no generic card background");
});

test("an icons-catalogue prop-icon stamp is allowed by the painter", () => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [], textContent: "", setAttribute(k, v) { this.at[k] = v; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  const icon = "prop-icon-bear-market-v1";
  paintChip({ sp: { kind: "chip", form: "stamp", at: 4, dur: 6, size: 260,
    icon, _catalogue: "icons", label: "BEAR MARKET", target: { kind: "point", x: .5, y: .5 } },
    t: 4.2, svg: { kids: [] }, el,
    A: { ["prop:" + icon]: "data:image/png;base64,approved-icon" },
    resolveTarget: () => ({ x: 960, y: 540, w: 0, h: 0 }), hash: () => .5,
    idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 });
  assert.deepEqual(made.map((e) => e.tag), ["g", "image", "text"]);
  assert.equal(made[1].at.href, "data:image/png;base64,approved-icon");
});

test("a non-badge finance prop refuses the chip path by name under E99 s87", () => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [], textContent: "", setAttribute(k, v) { this.at[k] = v; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  assert.throws(() => paintChip({ sp: { kind: "chip", form: "stamp", at: 4, dur: 6, size: 640,
    icon: "prop-liquidity-drain-pump-v1", _catalogue: "props", label: "LIQUIDITY DRAIN", target: { kind: "point", x: .5, y: .5 } },
    t: 4.2, svg: { kids: [] }, el,
    A: { "prop:prop-liquidity-drain-pump-v1": "data:image/png;base64,approved-prop" },
    resolveTarget: () => ({ x: 960, y: 540, w: 0, h: 0 }), hash: () => .5,
    idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 }), /prop-liquidity-drain-pump-v1.*E99 s87/);
  assert.equal(CHIP_STAMP.ICON_MAX_SIZE, 420);
  assert.equal(CHIP_STAMP.MAX_SIZE, 700);
  assert.equal(made.length, 0);
});

test("the stamp fails closed when the approved raster URI is absent", () => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [], textContent: "" }; made.push(e); return e; };
  paintChip({ sp: { kind: "chip", form: "stamp", at: 4, dur: 6, icon: "unapproved", label: "THING", target: { kind: "point", x: .5, y: .5 } },
    t: 4.2, svg: { kids: [] }, el, A: {}, resolveTarget: () => ({ x: 960, y: 540, w: 0, h: 0 }),
    hash: () => .5, idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 });
  assert.equal(made.length, 0);
});

// ---------------------------------------------------------------- P70 T1: the stamp form lands AS A STAMP (arrive: "stamp")
// E99 s87's arrival on the chip's opt-in raster form: the pose is stopaction's `stampXf`, every motion number STAMP_ARRIVAL's.
import * as CHIPMOD from "../../scripts/species/chip.mjs";
import { STAMP_ARRIVAL, STAMP_LAND, STAMP_TURN, stampXf, stampRing, stampExit } from "../../scripts/kinetics/stopaction.mjs";
const { CHIP_SEAL } = CHIPMOD;   // P70 T1b (E99 s121): the seal's dials, read off the module

const stampForm = (o = {}) => Object.assign({ kind: "chip", form: "stamp", at: 4, dur: 6, size: 260, _catalogue: "icons",
  icon: "prop-icon-gpu-ai-accelerator-v1", label: "NVIDIA", target: { kind: "point", x: 0.5, y: 0.5 } }, o);
// today's pose, written out from the law this slice must not move (chipLand + chipCrossF), for the byte-identity check
const springPose = (sp, t) => {
  const land = chipLand(t, +sp.at), cross = chipCrossF(sp, t);
  return { u: land.u, scale: land.scale, dy: land.dy, fade: land.fade, cross, strokes: chipStrokes(cross), dim: 1 - (1 - CHIP.DIM) * cross };
};
const stub = () => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [], textContent: "", setAttribute(k, v) { this.at[k] = v; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  return { made, el };
};
const paintAt = (sp, t, sc = { world: { kind: "ledger" } }) => {
  const { made, el } = stub();
  paintChip({ sp, t, sc, svg: { kids: [] }, el, A: { ["prop:" + sp.icon]: "data:image/png;base64,approved" },
    resolveTarget: () => ({ x: 960, y: 540, w: 0, h: 0 }), hash: () => 0.5, idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 });
  return made;
};

test("P70 T1: arrive stamp on the stamp form - the pose at t - at IS stampXf's (scale, turn, ink, fade, ring)", () => {
  assert.equal(typeof CHIPMOD.chipStampPose, "function", "chip.mjs exports the stamp pose");
  const sp = stampForm({ arrive: "stamp" });
  for (let i = 0; i <= 120; i++) {
    const t = sp.at + i * 0.01, ts = t - sp.at, p = chipPose(sp, t), sx = stampXf("ink", ts);   // the painter reads t - at
    assert.ok(near(p.scale, sx.scale, 1e-12), `scale at ${ts}`);
    assert.ok(near(p.rot, sx.rot, 1e-12), `rot at ${ts}`);
    assert.ok(near(p.ink, sx.ink, 1e-12), `ink at ${ts}`);
    assert.ok(near(p.fade, sx.opacity, 1e-12), `fade at ${ts}`);
    assert.deepEqual(p.ring, sx.ring, `ring at ${ts}`);   // P70 T1b (s121 (3)): stampXf throws it from the contact
    assert.deepEqual(p.ring, ts > STAMP_LAND.tc ? stampRing(ts - STAMP_LAND.tc) : null, `... stampRing on the contact's clock at ${ts}`);
  }
  assert.ok(near(chipPose(sp, sp.at).scale, STAMP_ARRIVAL.FROM, 1e-12), "it comes down from 2.1x");
  for (const ts of [STAMP_LAND.tc + 1e-9, 0.2, 0.5, 2]) assert.equal(chipPose(sp, sp.at + ts).scale, 1, `exactly 1 from tc (${ts})`);
  assert.ok(chipPose(sp, sp.at + STAMP_LAND.tc - 0.01).scale > 1, "... and not before");
  const rest = chipPose(sp, sp.at + STAMP_TURN.ts + 0.05);
  assert.ok(near(rest.rot, STAMP_ARRIVAL.LAND_DEG, 0.05) && rest.rot !== 0, "rests at LAND_DEG, off-square");
  let low = 0; for (let i = 0; i <= 400; i++) low = Math.min(low, chipPose(sp, sp.at + i / 400).rot);
  assert.ok(low < STAMP_ARRIVAL.LAND_DEG - 1, `the free rotation overshoots its rest (${low.toFixed(2)})`);
  assert.equal(chipPose(sp, sp.at).ink, STAMP_ARRIVAL.INK[0]);
  assert.ok(near(chipPose(sp, sp.at + 1).ink, STAMP_ARRIVAL.INK[1], 1e-12), "the ink eases back to 0.86");
  assert.equal(chipPose(sp, sp.at).ring, null, "no ring before the contact");
  assert.equal(chipPose(sp, sp.at + STAMP_LAND.tc - 0.01).ring, null, "nor on the way down (P70 T1b, s121 (3))");
  assert.equal(chipPose(sp, sp.at + STAMP_LAND.tc + STAMP_ARRIVAL.SHOCK_S + 0.01).ring, null, "and never held past its life");
});

test("P70 T1: the ring's peak is the compiler's fitted ring_to, else the source's RING_TO", () => {
  const ts = (4 + 0.3) - 4, fitted = chipPose(stampForm({ arrive: "stamp", ring_to: 1.4 }), 4 + 0.3).ring;
  const tr = ts - STAMP_LAND.tc;   // P70 T1b (s121 (3)): the ring's clock starts at the contact
  assert.deepEqual(fitted, stampRing(tr, { RING_TO: 1.4 }));
  assert.ok(fitted.r < stampRing(tr).r);
  assert.deepEqual(chipPose(stampForm({ arrive: "stamp" }), 4 + 0.3).ring, stampRing(tr));
});

test("P70 T1: the approach comes down from the compiler's fitted from_to, else the source's FROM - capped, never clipped", () => {
  const fitted = stampForm({ arrive: "stamp", from_to: 1.6 });
  assert.ok(near(chipPose(fitted, fitted.at).scale, 1.6, 1e-12), "the fall starts at the fitted scale");
  for (let i = 0; i <= 60; i++) {
    const t = fitted.at + i * 0.005;
    assert.ok(near(chipPose(fitted, t).scale, stampXf("ink", t - fitted.at, { FROM: 1.6 }).scale, 1e-12), `at ${t}`);
  }
  assert.equal(chipPose(fitted, fitted.at + STAMP_LAND.tc + 1e-9).scale, 1, "and lands at the same contact");
  assert.ok(near(chipPose(stampForm({ arrive: "stamp" }), 4).scale, STAMP_ARRIVAL.FROM, 1e-12));
});

test("P70 T1: the exit the landed mark owes runs INSIDE dur, on stampExit, and the ring is gone once it begins", () => {
  const sp = stampForm({ arrive: "stamp" }), out = sp.at + sp.dur - STAMP_ARRIVAL.EXIT_S;
  assert.equal(chipPose(sp, out).fade, 1, "at rest until the exit begins");
  for (const u of [0.25, 0.5, 0.75]) {
    const t = out + u * STAMP_ARRIVAL.EXIT_S;
    assert.ok(near(chipPose(sp, t).fade, 1 - stampExit(t - out), 1e-12), `exit at ${u}`);
  }
  assert.ok(near(chipPose(sp, sp.at + sp.dur).fade, 0, 1e-12), "gone when the window closes");
  const short = stampForm({ arrive: "stamp", dur: 0.5 });   // an exit that begins before the ring's life is spent
  assert.equal(chipPose(short, short.at + 0.2).ring, null, "no ring once the exit has begun");
});

test("P70 T1: WITHOUT arrive the pose is today's over 200 instants - the stamp form, the glyph chip, and a glyph chip that carries arrive", () => {
  const cases = [stampForm(), chip(), chip({ cross_at: 7 }), chip({ arrive: "stamp" }), stampForm({ arrive: "throw" }), stampForm({ ring_to: 1.2 })];
  for (const sp of cases) for (let i = 0; i < 200; i++) {
    const t = sp.at - 0.5 + i * 0.05;
    assert.deepEqual(chipPose(sp, t), springPose(sp, t), `${JSON.stringify(sp)} at ${t}`);
  }
});

test("P70 T1: the painter lands a stamped chip with its ring UNDER the mark, turned, and its label at the s90 floor", () => {
  assert.equal(CHIP_STAMP.LABEL_FLOOR, 59.08, "the phone floor [DERIVED: ledger_page.CARD_TYPE_PX, 12 * 1920 / 390]");
  const sp = stampForm({ arrive: "stamp", paint: [0, 0.1, 1, 0.9] });
  const mid = paintAt(sp, sp.at + 0.254);   // contact + 0.10 s: the ring radiating, the rotation still off its rest
  assert.deepEqual(mid.map((e) => e.tag), ["circle", "g", "circle", "circle", "image", "text"]);   // P70 T1b: the seal's two rings in the mark's group
  const [ring, g, , , art, lab] = mid;
  assert.equal(ring.cls, "chipstampring");
  assert.equal(ring.at.stroke, CHIP_SEAL.GOLD, "P70 T1c (E99 s127 (2)): the seal's gold, the shockwave in the seal's own colour");
  assert.equal(ring.at.fill, "none");
  const rg = stampRing(0.254 - STAMP_LAND.tc), r0 = 0.5 * Math.hypot(260, 260 * 0.8);   // P70 T1b: the ring's clock from the contact
  const R0 = (r0 + CHIP_SEAL.GAP_PX) * CHIP_SEAL.SRC_R / CHIP_SEAL.INNER_R;   // ... and its base the SEAL's outer ring (s121 (1))
  assert.equal(ring.at.r, (R0 * rg.r).toFixed(1), "the seal's own outer radius x the ring's multiplier - thrown from the seal's border, as the source's is");
  assert.equal(ring.at["stroke-width"], rg.width.toFixed(2));
  assert.equal(ring.at.opacity, rg.alpha.toFixed(3));
  assert.equal(ring.at.cx, "960.0");
  assert.equal(ring.at.cy, "540.0", "about the painted centre - here the square's own");
  // P70 T1b (fix 3): the receiver's dip runs from the CONTACT, so 0.10 s after it the mark rides stampXf's dip exactly
  assert.equal(g.at.transform, "translate(960.0 " + (540 + stampXf("ink", 0.254).y).toFixed(1) + ") rotate(-10.39) scale(1.0000)");
  assert.equal(art.cls, "chipstampart");
  assert.match(lab.at.style, /font-size:59\.08px/);
  assert.equal(lab.at.y, (130 + 28 * 59.08 / 48).toFixed(1), "the gap scales with the floor");
  const plate = paintAt(sp, sp.at + 0.254, { world: { asset_id: "plate-plain" } });
  assert.equal(plate[0].at.stroke, CHIP_SEAL.GOLD, "P70 T1c: on any other world too - never inked from the ground");
  const two = paintAt(stampForm({ arrive: "stamp", label: "NVIDIA\nCHIPS" }), 4 + 2);
  assert.equal(two.filter((e) => e.tag === "tspan")[1].at.dy, +(52 * 59.08 / 48).toFixed(2), "and the line step");
  assert.deepEqual(paintAt(sp, sp.at + 2).map((e) => e.tag), ["g", "circle", "circle", "image", "text"], "the ring is never held (the seal stays)");
});

test("P70 T1: a stamp-form chip WITHOUT arrive paints exactly what it painted - 48 px label, no ring, no turn", () => {
  const made = paintAt(stampForm(), 4.2);
  assert.deepEqual(made.map((e) => e.tag), ["g", "image", "text"]);
  assert.doesNotMatch(made[0].at.transform, /rotate/);
  assert.match(made[2].at.style, /font-size:48px/);
  assert.equal(made[2].at.y, (130 + 28).toFixed(1));
  assert.equal(made[2].at.x, 0);
});

// ---------------------------------------------------------------- P70 T1b (E99 s121, s123): a seal-type stamp is a SEAL, and gold
// The operator: "the stamp needs to have a solid border"; "part of the reason that stamp works is the color". badge-stamp.tsx's
// seal, read off its lines (r = 50): the outer ring at r, stroke 3.4, ink (:172-180); the inner ring at r - 6, stroke 1.2,
// ink x 0.7 (:181-189); ring text 7.4 / letterSpacing 1.6 on the top arc at r - 12 and the bottom arc at r - 14 with dy 6.4,
// ink x 0.9 (:137-149, :191-220); the colour #E8B86D (:57). Both rings are in the MARK's group, so they land, rest and leave
// with it - the impact ring radiates from the outer one and is gone.
const sealOf = (sp, side = 260) => {
  const S = CHIP_SEAL, rc = CHIPMOD.chipStampPaint(sp, side).r;
  const R = Number.isFinite(+sp.seal_r) ? +sp.seal_r : (rc + S.GAP_PX) * S.SRC_R / S.INNER_R;
  return { rc, R, u: R / S.SRC_R, rIn: R * S.INNER_R / S.SRC_R };
};

test("P70 T1b: the seal's dials ARE the source's, each read off its own line", () => {
  assert.equal(CHIP_SEAL.SRC_R, 50);            /* :127 const r = 50 */
  assert.equal(CHIP_SEAL.INNER_R, 44);          /* :184 r - 6 */
  assert.equal(CHIP_SEAL.OUTER_W, 3.4);         /* :178 */
  assert.equal(CHIP_SEAL.INNER_W, 1.2);         /* :187 */
  assert.equal(CHIP_SEAL.INNER_A, 0.7);         /* :188 ink * 0.7 */
  assert.equal(CHIP_SEAL.TEXT_A, 0.9);          /* :198 / :214 ink * 0.9 */
  assert.equal(CHIP_SEAL.TEXT_SIZE, 7.4);       /* :194 */
  assert.equal(CHIP_SEAL.TEXT_TRACK, 1.6);      /* :196 */
  assert.equal(CHIP_SEAL.TOP_R, 38);            /* :142 r - 12 */
  assert.equal(CHIP_SEAL.BOTTOM_R, 36);         /* :147 r - 14 */
  assert.equal(CHIP_SEAL.BOTTOM_DY, 6.4);       /* :212 */
  assert.equal(CHIP_SEAL.GOLD, "#E8B86D", "E99 s123: the source's own default colour, ONE dial");
  assert.equal(CHIP_SEAL.GAP_PX, 12, "the build's STAMP_RING_GAP_PX - the least page between a mark and a ring");
});

test("P70 T1b (s123): the seal is GOLD on the dark ground, darkened on the cream until it reads - the sunflower is not the seal's", () => {
  assert.equal(CHIPMOD.sealGold({}), CHIP_SEAL.GOLD, "gold on the dark ground, as the reference");
  assert.ok(CHIPMOD.sealContrast(CHIP_SEAL.GOLD, CHIP_SEAL.GROUND.dark) > 7, "#E8B86D on the charcoal is 7.27:1");
  assert.ok(CHIPMOD.sealContrast(CHIP_SEAL.GOLD, CHIP_SEAL.GROUND.light) < CHIP_SEAL.CONTRAST_MIN, "... and 1.48:1 on the cream - it would not read");
  const dark = CHIPMOD.sealGold({ ink: "charcoal" });
  assert.equal(dark, "#A07F4B", "the gold's channels scaled down in 1 % steps (x0.69)");
  assert.ok(CHIPMOD.sealContrast(dark, CHIP_SEAL.GROUND.light) >= CHIP_SEAL.CONTRAST_MIN, "until it holds 3:1 on the cream");
  assert.notEqual(CHIP_SEAL.GOLD.toUpperCase(), "#F5B72E", "the sunflower stays the callout / focus yellow - a separate token");
  assert.equal(CHIPMOD.sealGold({ ink: "charcoal" }, "#C79E5E"), "#9F7E4B", "the dial's other candidate darkens the same way");
});

test("P70 T1b (s121 (1)): a stamped chip lands AS A SEAL - the solid outer ring and the thin inner ring ride the mark, in gold", () => {
  const sp = stampForm({ arrive: "stamp", paint: [0, 0.1, 1, 0.9], ink: "charcoal" });
  const mid = paintAt(sp, sp.at + 0.254), g = mid[1], seal = CHIPMOD.chipSeal(sp, 260), want = sealOf(sp);
  assert.ok(near(seal.R, want.R, 1e-9) && near(seal.rIn, want.rIn, 1e-9), "chipSeal is the geometry the source's ratios give");
  const [outer, inner] = g.kids.filter((e) => e.tag === "circle");
  assert.ok(outer && inner, "both rings are children of the MARK's group - they land, rest and leave with it");
  assert.equal(outer.cls, "chipseal"); assert.equal(inner.cls, "chipsealin");
  for (const c of [outer, inner]) {
    assert.equal(c.at.cx, 0); assert.equal(c.at.cy, 0); assert.equal(c.at.fill, "none");
    assert.equal(c.at.stroke, "#A07F4B", "the seal's gold, darkened on the light ground the row names");
  }
  assert.equal(outer.at.r, want.R.toFixed(1));
  assert.equal(outer.at["stroke-width"], (want.R * 3.4 / 50).toFixed(2), "SOLID and thick: 3.4 of 50");
  assert.equal(inner.at.r, want.rIn.toFixed(1));
  assert.equal(inner.at["stroke-width"], (want.R * 1.2 / 50).toFixed(2), "thin: 1.2 of 50");
  assert.ok(want.rIn - want.rc >= CHIP_SEAL.GAP_PX - 1e-9, "the mark and its name sit inside the inner ring, the gap clear");
  assert.equal(mid[0].cls, "chipstampring");
  assert.ok(+mid[0].at.r > want.R, "the impact ring is outside the seal - thrown from its border");
  const rest = paintAt(sp, sp.at + 2);
  assert.equal(rest.filter((e) => e.cls === "chipstampring").length, 0, "the impact ring is spent");
  assert.equal(rest.filter((e) => e.cls === "chipseal" || e.cls === "chipsealin").length, 2, "the seal rests with the mark");
  const out = sp.at + sp.dur - STAMP_ARRIVAL.EXIT_S + 0.3, leaving = paintAt(sp, out);
  assert.equal(leaving.filter((e) => e.cls === "chipseal").length, 1, "and leaves on the mark's own exit");
  assert.ok(near(+leaving[0].at.opacity, 1 - stampExit(0.3), 2e-3), "inside the group that fades");
  const dark = paintAt(stampForm({ arrive: "stamp" }), 6);
  assert.equal(dark.find((e) => e.cls === "chipseal").at.stroke, CHIP_SEAL.GOLD, "gold as it is on the dark ground");
  assert.match(dark.find((e) => e.cls === "chipstamplab").at.style, /fill:#E8B86D;/, "the NAME is the seal's gold");
  assert.match(dark.find((e) => e.cls === "chipstamplab").at.style, /stroke:#25313C/, "... on its charcoal keyline");
});

test("P70 T1b (fix 6): the seal's radius is the compiler's `seal_r` - the room the authored mark reserved - whatever the grown art", () => {
  const sp = stampForm({ arrive: "stamp", size: 335.2, seal_r: 246.4, paint: [0.0089, 0.0093, 0.9911, 1.17] });
  const seal = CHIPMOD.chipSeal(sp, 335.2);
  assert.equal(seal.R, 246.4, "the seal stays the size the room gave it");
  assert.ok(near(seal.rIn, 246.4 * 44 / 50, 1e-9));
  const m = paintAt(sp, sp.at + 2);
  assert.equal(m.find((e) => e.cls === "chipstampart").at.width, "335.2", "the art is drawn at the grown side");
  assert.equal(m.find((e) => e.cls === "chipseal").at.r, "246.4");
});

// the group's LINEAR part as the SVG composes it (rotate . scale . matrix), and a circle of radius r's half-extents under it
const groupLinear = (transform) => {
  const rot = +/rotate\(([-0-9.]+)\)/.exec(transform)[1] * Math.PI / 180, s = +/scale\(([-0-9.]+)\)/.exec(transform)[1];
  const m = /matrix\(([^)]+)\)/.exec(transform), [a, b, c, d] = m ? m[1].trim().split(/\s+/).map(Number) : [1, 0, 0, 1];
  const R = [[Math.cos(rot) * s, -Math.sin(rot) * s], [Math.sin(rot) * s, Math.cos(rot) * s]], M = [[a, c], [b, d]];
  return [[R[0][0] * M[0][0] + R[0][1] * M[1][0], R[0][0] * M[0][1] + R[0][1] * M[1][1]],
          [R[1][0] * M[0][0] + R[1][1] * M[1][0], R[1][0] * M[0][1] + R[1][1] * M[1][1]]];
};
const circleExtents = (L, r) => [r * Math.hypot(L[0][0], L[0][1]), r * Math.hypot(L[1][0], L[1][1])];

test("P70 T1b (the parent's R3): a SEAL does not squash - its width and height stay equal from the contact to contact + 0.1 s", () => {
  const sp = stampForm({ arrive: "stamp", paint: [0, 0.1, 1, 0.9], ink: "charcoal" });
  const tc = STAMP_LAND.tc;
  let dipped = 0, rang = 0;
  for (let i = 0; i <= 100; i++) {   // every millisecond, so the 24 fps squash frame (contact + 0.021 .. + 0.063 s) is crossed
    const t = sp.at + tc + i / 1000, p = chipPose(sp, t);
    assert.equal(p.alpha, 0, `no squash on the seal's pose at contact + ${(i / 1000).toFixed(3)} s`);
    const g = paintAt(sp, t)[1], outer = g.kids.find((e) => e.cls === "chipseal");
    assert.doesNotMatch(g.at.transform, /matrix/, `no squash tensor on the mark's group at contact + ${(i / 1000).toFixed(3)} s`);
    const [w, h] = circleExtents(groupLinear(g.at.transform), +outer.at.r);
    assert.ok(near(w, h, 1e-9), `the seal is round at contact + ${(i / 1000).toFixed(3)} s: ${w.toFixed(3)} x ${h.toFixed(3)}`);
    dipped = Math.max(dipped, p.dy); if (p.ring) rang++;
  }
  // ... and the rest of the hit stays: the page's dip, the impact ring and the ink easing back, as stampXf("ink") has them
  const sx = stampXf("ink", tc + 0.05);
  assert.ok(near(chipPose(sp, sp.at + tc + 0.05).dy, sx.y, 1e-12) && sx.y > 0, "the dip is the ink mass's, from the contact");
  assert.ok(dipped > 1 && rang > 90, `the dip (${dipped.toFixed(2)} px) and the ring (${rang} of 101 instants) are kept`);
  assert.ok(chipPose(sp, sp.at + tc + 0.05).ink < STAMP_ARRIVAL.INK[0], "the ink is easing back after the hit");
  // a BARE PROP (the dock's stampXf at its own mass) keeps its squash frame - only the seal is rigid
  assert.ok(stampXf("ink", tc + 0.04).alpha > 0.2, "the dock stamp's squash frame is untouched");
});

test("P70 T1b (s121 (2)): no seal anywhere else - the unstamped stamp form, a glyph chip", () => {
  assert.equal(CHIPMOD.chipSeal(stampForm(), 260), null, "the stamp FORM on its spring is a sticker being placed, not a stamp");
  assert.equal(CHIPMOD.chipSeal(chip(), 260), null);
  assert.equal(paintAt(stampForm(), 6).filter((e) => /chipseal/.test(e.cls || "")).length, 0);
  assert.equal(paintAt(stampForm({ ring_text: "AI" }), 6).filter((e) => e.cls === "chipsealglyph").length, 0, "ring text is the seal's");
  assert.doesNotMatch(paintAt(stampForm(), 6).find((e) => e.cls === "chipstamplab").at.style, /E8B86D/, "an unstamped name keeps its ink");
});

test("P70 T1b (s121 (4)): the ink eases back ON THE MARK - the seal, its text and its name; never a wash over the picture", () => {
  const sp = stampForm({ arrive: "stamp", ring_text: "AI ACCELERATOR", ring_text_bottom: "GPU" });
  const at = (t) => {
    const m = paintAt(sp, t);
    return { o: m.find((e) => e.cls === "chipseal"), i: m.find((e) => e.cls === "chipsealin"), tx: m.filter((e) => e.cls === "chipsealtext"),
             lab: m.find((e) => e.cls === "chipstamplab"), art: m.find((e) => e.cls === "chipstampart") };
  };
  const hit = at(sp.at + STAMP_LAND.tc), later = at(sp.at + 1);
  assert.equal(hit.o.at.opacity, "1.000", "heavy at the hit");
  assert.equal(hit.lab.at.opacity, "1.000");
  assert.equal(later.o.at.opacity, (0.86).toFixed(3), "0.86 once the pressure is off");
  assert.equal(later.i.at.opacity, (0.86 * 0.7).toFixed(3));
  assert.equal(later.tx.length, 2);
  for (const e of later.tx) assert.equal(e.at.opacity, (0.86 * 0.9).toFixed(3));
  assert.equal(later.lab.at.opacity, (0.86).toFixed(3), "the name is stamped ink too");
  assert.equal(later.art.at.opacity, undefined, "the PICTURE is the payload: no ink over it");
});

test("P70 T1b (fixes 1, 2): ring text at the SOURCE's proportion, glyph by glyph, EVENLY spaced and CENTRED on each arc's axis", () => {
  const sp = stampForm({ arrive: "stamp", ring_text: "AI ACCELERATOR", ring_text_bottom: "GPU" }), w = sealOf(sp), S = CHIP_SEAL;
  const seal = CHIPMOD.chipSeal(sp, 260);
  assert.ok(near(seal.size, S.TEXT_SIZE * w.u, 1e-9), "7.4 of r = 50 - the text never widens the seal");
  assert.ok(near(seal.R, sealOf(stampForm({ arrive: "stamp" })).R, 1e-9), "the seal is the size it is without text");
  assert.ok(near(seal.track, S.TEXT_TRACK * w.u, 1e-9));
  const m = paintAt(sp, sp.at + 2), groups = m.filter((e) => e.cls === "chipsealtext");
  assert.equal(groups.length, 2);
  assert.equal(m.filter((e) => e.tag === "textPath" || e.tag === "defs").length, 0, "no textPath: each glyph is placed");
  for (const [arc, grp, side] of [[seal.top, groups[0], 1], [seal.bottom, groups[1], -1]]) {
    const adv = [...arc.text].map((ch) => S.ADVANCE_EM[ch] * seal.size);
    const L = adv.reduce((a, v) => a + v, 0) + (adv.length - 1) * seal.track;
    assert.ok(near(arc.len, L, 1e-9), "the line's length is the measured advances plus the tracking between glyphs");
    /* CENTRED: the first glyph's left edge and the last glyph's right edge are symmetric about the axis */
    const first = arc.glyphs[0].a * arc.r - adv[0] / 2, last = arc.glyphs.at(-1).a * arc.r + adv.at(-1) / 2;
    assert.ok(near(first, -last, 1e-9), `centred on its axis: ${first.toFixed(2)} / ${last.toFixed(2)}`);
    /* EVEN: consecutive centres are exactly half of each advance + the tracking apart, along the arc */
    for (let i = 1; i < adv.length; i++) {
      const gap = (arc.glyphs[i].a - arc.glyphs[i - 1].a) * arc.r;
      assert.ok(near(gap, adv[i - 1] / 2 + seal.track + adv[i] / 2, 1e-9), `glyph ${i} spaced by the advances`);
    }
    assert.ok(L <= Math.PI * arc.r, "within its half-arc");
    const drawn = grp.kids.filter((e) => e.cls === "chipsealglyph");
    assert.equal(drawn.length, [...arc.text].filter((c) => c.trim()).length, "a space is an advance, not a glyph");
    const rho = side > 0 ? arc.r : arc.r + arc.dy;
    const g0 = arc.glyphs.find((gl) => gl.ch.trim()), d0 = drawn[0];
    assert.equal(d0.at.x, (rho * Math.sin(g0.a)).toFixed(2));
    assert.equal(d0.at.y, (side * -rho * Math.cos(g0.a)).toFixed(2), side > 0 ? "the top's baseline on its arc" : "the bottom's pushed out by dy");
    const deg = (side > 0 ? g0.a : -g0.a) * 180 / Math.PI;
    assert.match(d0.at.transform, new RegExp("^rotate\\(" + deg.toFixed(3).replace(".", "\\.")), "each glyph turned to stand on the arc, reading left to right");
    assert.ok(+d0.at.x < 0, "the line STARTS on the left - left to right on both arcs");
    assert.equal(d0.at["text-anchor"], "middle");
    assert.match(grp.at.style, new RegExp("font-size:" + seal.size.toFixed(2).replace(".", "\\.") + "px"));
  }
  assert.equal(paintAt(stampForm({ arrive: "stamp", ring_text: "AI" }), 6).filter((e) => e.cls === "chipsealtext").length, 1, "either arc is optional");
  assert.equal(paintAt(stampForm({ arrive: "stamp" }), 6).filter((e) => e.cls === "chipsealtext").length, 0, "absent = no ring text");
});

/* P70 T1c (E99 s127 (2)): A SEAL'S SHOCKWAVE IS THE SEAL'S GOLD - the reference's is its seal's colour - darkened on the
   cream by the seal's own contrast law, and never inked from the ground. (s128): the seal is OPEN - no fill anywhere in
   the mark's group but the picture and the name, so the chart shows through it. */
test("T1c: the seal's impact ring is CHIP_SEAL.GOLD on the dark ground and the seal's darkened gold on the cream - on any world", async () => {
  const { CHIP_SEAL, sealGold } = await import("../../scripts/species/chip.mjs");
  const dark = stampForm({ arrive: "stamp", ink: "cream" }), light = stampForm({ arrive: "stamp", ink: "charcoal" });
  for (const sc of [{ world: { kind: "ledger" } }, { world: { asset_id: "plate-plain" } }, { world: { asset_id: "plate-charcoal" } }]) {
    const d = paintAt(dark, dark.at + 0.254, sc).find((e) => e.cls === "chipstampring");
    const l = paintAt(light, light.at + 0.254, sc).find((e) => e.cls === "chipstampring");
    assert.equal(d.at.stroke, CHIP_SEAL.GOLD, `the gold as it is on the dark ground (${JSON.stringify(sc.world)})`);
    assert.equal(d.at.stroke, "#E8B86D", "E99 s127 (1): the seal is #E8B86D");
    assert.equal(l.at.stroke, sealGold(light), "... and on the cream, the seal's own darkened gold");
    assert.equal(l.at.stroke, "#A07F4B");
    const seal = paintAt(dark, dark.at + 0.254, sc).find((e) => e.cls === "chipseal");
    assert.equal(d.at.stroke, seal.at.stroke, "the shockwave is the seal's own colour, as the reference's is");
  }
  assert.equal(CHIP_STAMP.RING_INK, undefined, "no ground ink is left on the chip: a stamped chip is always a seal");
});

test("T1c (E99 s128): the seal is OPEN - nothing in the mark's group is filled but the picture and the name", () => {
  for (const extra of [{}, { ring_text: "AI ACCELERATOR", ring_text_bottom: "GPU" }]) {
    const sp = stampForm(Object.assign({ arrive: "stamp", ink: "cream" }, extra));
    for (const t of [sp.at + 0.254, sp.at + 2]) {
      const made = paintAt(sp, t);
      const circles = made.filter((e) => e.tag === "circle");
      assert.ok(circles.length >= 2, "the seal's two rings are drawn");
      for (const c of circles) assert.equal(c.at.fill, "none", `${c.cls} is a stroke, never a disc`);
      const filled = made.filter((e) => !["circle", "g", "image", "text", "tspan"].includes(e.tag));
      assert.deepEqual(filled.map((e) => e.tag), [], "no rect, path or backdrop under the seal");
      for (const g of made.filter((e) => e.tag === "g")) {
        assert.equal(g.at.fill, undefined, "the group carries no fill");
        assert.equal(g.at.filter, undefined, "... and no filter");
      }
    }
  }
});

// ---------------------------------------------------------------- P71 T12: THE STATES - lit (and pulse), tick, sell / buy
// Bravos A36 / F3 (the active tile glows, BUB #20), A14 (the check), A59 (SELL / BUY tabs, JPN 04:08 / 05:34). Each lands on
// its word and each is a pure function of t; absent, the chip paints exactly what it painted (chipPose is today's).
const { chipTickF, chipTickStrokes, chipCheckPose, chipLitF, chipPulseOnsets, chipTabPose, chipStates } = CHIPMOD;
const glyphCtx = (sp, t) => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [], textContent: "", setAttribute(k, v) { this.at[k] = v; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  paintChip({ sp, t, svg: { kids: [] }, el, A: { "icon:factory": JSON.stringify({ vb: [0, 0, 24, 24], el: [{ t: "path", a: { d: "M12 16h.01" } }] }) },
    resolveTarget: () => ({ x: 100, y: 200, w: 0, h: 0 }), drawOn: (p, k) => p.setAttribute("stroke-dashoffset", k.toFixed(3)),
    hash: () => 0.5, idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 });
  return made;
};

test("T12: the states are the module's exports, and chipPose stays today's for a chip that carries them", () => {
  for (const f of [chipTickF, chipTickStrokes, chipCheckPose, chipLitF, chipPulseOnsets, chipTabPose, chipStates]) assert.equal(typeof f, "function");
  const cases = [chip({ state: "lit" }), chip({ state: "lit", pulse: true }), chip({ tick_at: 7 }), chip({ tab: "sell", tab_at: 6 }),
                 chip({ tab: "buy" })];
  for (const sp of cases) for (let i = 0; i < 120; i++) {
    const t = sp.at - 0.5 + i * 0.05;
    assert.deepEqual(chipPose(sp, t), springPose(sp, t), `${JSON.stringify(sp)} at ${t}`);
  }
});

test("T12 (acceptance 3): the tick is 0 until tick_at, 1 CROSS_S later, and absent without tick_at", () => {
  const sp = chip({ tick_at: 7 });
  assert.equal(chipTickF(sp, 6.99), 0);
  assert.ok(near(chipTickF(sp, 7 + CHIP.CROSS_S / 2), 0.5, 1e-12));
  assert.equal(chipTickF(sp, 7 + CHIP.CROSS_S), 1);
  assert.equal(chipTickF(sp, 30), 1);
  assert.equal(chipTickF(chip(), 30), 0, "no tick_at, never ticked");
  assert.equal(chipTickF(chip({ cross_at: 7 }), 30), 0, "a cross is not a tick");
  assert.equal(chipCrossF(sp, 30), 0, "... and a tick is not a cross");
});

test("T12 (acceptance 3): the check draws in TWO strokes, split by their lengths - one hand through the knee", () => {
  const K = CHIP.TICK, l1 = Math.hypot(K[1][0] - K[0][0], K[1][1] - K[0][1]), l2 = Math.hypot(K[2][0] - K[1][0], K[2][1] - K[1][1]);
  assert.ok(l2 > l1 * 1.5, "the up stroke is the long one");
  assert.ok(K[1][1] > K[0][1] && K[2][1] < K[1][1], "down to the knee, then up: a check, not a slash");
  assert.deepEqual(chipTickStrokes(0), [0, 0]);
  assert.deepEqual(chipTickStrokes(1), [1, 1]);
  const knee = l1 / (l1 + l2);
  const at = chipTickStrokes(knee);
  assert.ok(near(at[0], 1, 1e-12) && near(at[1], 0, 1e-12), `the first stroke ends at the knee: ${at}`);
  let prev = [0, 0];
  for (let i = 0; i <= 100; i++) {
    const s = chipTickStrokes(i / 100);
    assert.ok(s[0] >= prev[0] && s[1] >= prev[1], "only ever forward");
    assert.ok(s[1] === 0 || s[0] === 1, "the second stroke starts only once the first is done");
    prev = s;
  }
});

test("T12 (fix 1, HIS 06:13): the check is a DISC BADGE centred ON the card's top edge, CHECK_D of the card - the icon is never covered", () => {
  assert.equal(CHIP.CHECK_D, 0.224, "Bravos HIS 06:13: 37 px discs on 164 px tiles");
  const made = glyphCtx(chip({ tick_at: 7 }), 7 + CHIP.CROSS_S * 0.8);
  const body = made.filter((e) => e.tag === "g")[1];
  assert.equal(body.at.opacity, "1.000", "the card is not dimmed");
  const cg = made.find((e) => e.cls === "chipcheck");
  assert.ok(cg, "the badge group");
  assert.equal(made[0].kids[made[0].kids.length - 1], cg, "drawn last, over the card's edge");
  const settled = glyphCtx(chip({ tick_at: 7 }), 7 + 2 * CHIP.LAND_S).find((e) => e.cls === "chipcheck");
  assert.equal(settled.at.transform, "translate(0 " + (-CHIP.SIZE / 2).toFixed(1) + ") scale(1.0000)", "centred ON the top edge, settled");
  const disc = cg.kids[0];
  assert.equal(disc.cls, "chipcheckdisc");
  assert.equal(+disc.at.r, +(CHIP.CHECK_D * CHIP.SIZE / 2).toFixed(1));
  assert.ok(disc.at.style.includes("fill:" + CHIP.TICK_INK));
  const marks = made.filter((e) => e.cls === "chipcheckmark");
  assert.equal(marks.length, 2, "the check in two strokes");
  for (const p of marks) assert.ok(p.at.style.includes("stroke:" + CHIP.CHECK_MARK), p.at.style);
  assert.equal(marks[0].at["stroke-dashoffset"], "1.000", "the short stroke is in");
  assert.ok(+marks[1].at["stroke-dashoffset"] > 0 && +marks[1].at["stroke-dashoffset"] < 1, "the long one drawing");
  assert.equal(made.filter((e) => e.cls === "sq").length, 0, "no stroke across the icon");
  const r = CHIP.CHECK_D * CHIP.SIZE / 2;
  assert.ok(r < CHIP.SIZE / 2 - CHIP.GLYPH / 2, "the badge's lower half stays above the glyph's box");
  assert.equal(glyphCtx(chip({ tick_at: 7 }), 6.9).filter((e) => e.cls === "chipcheck").length, 0, "nothing before its word");
  assert.ok(sealContrastOf(CHIP.CHECK_MARK, CHIP.TICK_INK) >= 4.5, "the check reads on the disc");
});

test("T12 (fix 1): the badge springs in on tick_at on the BADGE SPRING (chipLand's clock)", () => {
  const sp = chip({ tick_at: 7 });
  for (let i = 0; i <= 40; i++) {
    const t = 6.8 + i * 0.025, ck = chipCheckPose(sp, t), land = chipLand(t, 7);
    assert.deepEqual([ck.u, ck.scale, ck.dy, ck.fade], [land.u, land.scale, land.dy, land.fade], `t=${t}`);
    assert.deepEqual(ck.strokes, chipTickStrokes(chipTickF(sp, t)));
  }
  assert.equal(chipCheckPose(chip(), 9), null);
  assert.equal(chipCheckPose(sp, 7, 110).d, CHIP.CHECK_D * 110, "the badge scales with the card (the phone card)");
});

test("T12 (acceptance 2): lit HOLDS - its level is the landing's fade, then exactly 1 for as long as the chip stands", () => {
  const sp = chip({ state: "lit" });
  assert.equal(chipLitF(chip(), 6), 0, "a chip that is not lit has no halo");
  assert.equal(chipLitF(chip({ state: "crossed" }), 6), 0);
  assert.equal(chipLitF(sp, sp.at - 0.1), 0, "nothing before its word");
  for (let i = 0; i <= 20; i++) {
    const t = sp.at + i * CHIP.FADE_S / 20;
    assert.ok(near(chipLitF(sp, t), chipLand(t, sp.at).fade, 1e-12), "the halo comes up with the landing's fade");
  }
  for (let i = 0; i < 200; i++) assert.equal(chipLitF(sp, sp.at + 2 * CHIP.FADE_S + i * 0.03), 1, "a held halo: no blink, no drift");   // past the fade's float edge
  assert.deepEqual(chipPulseOnsets(sp), [], "no pulse, no onsets");
  assert.deepEqual(chipPulseOnsets(chip({ pulse: true })), [], "a pulse on a chip that is not lit blinks nothing");
});

test("T12 (acceptance 2): pulse BLINKS the lit halo PULSE_N times from the settle, down to PULSE_LOW and back, then holds", () => {
  const sp = chip({ state: "lit", pulse: true });
  const ons = chipPulseOnsets(sp);
  assert.equal(ons.length, CHIP.PULSE_N);
  ons.forEach((a, k) => assert.ok(near(a, sp.at + CHIP.LAND_S + k * CHIP.PULSE_S, 1e-12)));
  for (const a of ons) {
    assert.ok(near(chipLitF(sp, a), 1, 1e-12), "each blink begins from the full halo");
    assert.ok(near(chipLitF(sp, a + CHIP.PULSE_S / 2), CHIP.PULSE_LOW, 1e-12), "... dips to PULSE_LOW at its middle");
    assert.ok(chipLitF(sp, a + CHIP.PULSE_S * 0.25) < 1 && chipLitF(sp, a + CHIP.PULSE_S * 0.25) > CHIP.PULSE_LOW);
  }
  const end = ons[ons.length - 1] + CHIP.PULSE_S;
  for (let i = 0; i < 50; i++) assert.equal(chipLitF(sp, end + i * 0.1), 1, "after the last blink it holds");
  assert.equal(chipLitF(sp, ons[0] - 0.01), 1, "between the settle and the first blink it is lit");
});

test("T12 (acceptance 4): the tab lands on tab_at on the BADGE SPRING (chipLand's clock), else with the chip", () => {
  const sp = chip({ tab: "sell", tab_at: 7 });
  for (let i = 0; i <= 40; i++) {
    const t = 6.8 + i * 0.025, tab = chipTabPose(sp, t), land = chipLand(t, 7);
    assert.deepEqual([tab.u, tab.scale, tab.dy, tab.fade], [land.u, land.scale, land.dy, land.fade], `t=${t}`);
  }
  assert.equal(chipTabPose(sp, 6.99).fade, 0, "nothing before its word");
  assert.equal(chipTabPose(chip({ tab: "buy" }), 4.3).at, 4, "no tab_at: it lands with the chip");
  assert.equal(chipTabPose(chip(), 9), null);
  assert.equal(chipTabPose(chip({ tab: "hold" }), 9), null, "an unknown tab is the compiler's refusal, and paints nothing");
  assert.equal(chipTabPose(chip({ tab: 120 }), 9), null);
});

test("T12 (acceptance 4, fix 1): SELL in the negative ink, BUY in the positive, the word at the s90 floor, the PILL hugging it", () => {
  const s = chipTabPose(chip({ tab: "sell" }), 9), b = chipTabPose(chip({ tab: "buy" }), 9);
  assert.equal(s.fill, CHIP.TAB_INK.sell);
  assert.equal(b.fill, CHIP.TAB_INK.buy);
  assert.equal(CHIP.TAB_INK.sell, "#FF4D4D");
  assert.equal(CHIP.TAB_INK.buy, "#3DDC84");
  assert.deepEqual([s.word, b.word], ["SELL", "BUY"]);
  assert.deepEqual(Object.keys(CHIP.TAB_EM).sort(), Object.keys(CHIP.TAB_INK).map((k) => k.toUpperCase()).sort(), "every tab word has its measured advance");
  assert.ok(CHIP.TAB_TYPE >= 59.08, "the s90 floor");
  for (const tab of [s, b]) assert.ok(near(tab.w, CHIP.TAB_EM[tab.word] * CHIP.TAB_TYPE + 2 * CHIP.TAB_PAD, 1e-9), "the pill hugs its word");
  assert.ok(b.w <= CHIP.SIZE, "BUY is no wider than the card");
  assert.ok((s.w - CHIP.SIZE) / 2 <= 6, `SELL overhangs a few px at most: ${(s.w - CHIP.SIZE) / 2}`);
  const cap = CHIP.TAB_TYPE * 0.727, R = CHIP.TAB_H / 2;
  assert.ok(CHIP.TAB_H > cap + 20, "the pill holds its word's caps with room");
  // the capsule's round end clears the caps at the word's first and last column (TAB_PAD in from the end)
  assert.ok(Math.sqrt(R * R - (R - CHIP.TAB_PAD) ** 2) > cap / 2, "the caps sit inside the capsule's ends");
  assert.ok(CHIP.SIZE / 2 - R > CHIP.GLYPH / 2 - 3, "the pill's lower half stops at the glyph's box");
  assert.ok(sealContrastOf(CHIP.TAB_TEXT, CHIP.TAB_INK.sell) >= 3 && sealContrastOf(CHIP.TAB_TEXT, CHIP.TAB_INK.buy) >= 3,
    "the word reads on both fills (WCAG large text 3:1)");
  for (const fill of Object.values(CHIP.TAB_INK))
    assert.ok(sealContrastOf(CHIP.TAB_TEXT, fill) > sealContrastOf("#F2F2F2", fill), "charcoal beats chalk on " + fill);
});
const sealContrastOf = (a, b) => CHIPMOD.sealContrast(a, b);

test("T12: the painter - the halo is the body's FIRST child (under the card, dimming with it); the tab is the group's LAST", () => {
  const lit = glyphCtx(chip({ state: "lit" }), 9);
  const body = lit.filter((e) => e.tag === "g")[1];
  assert.equal(body.kids[0].cls, "chiphalo");
  assert.equal(body.kids[1].cls, "chipcard");
  const halo = body.kids[0];
  assert.equal(halo.at.opacity, "1.000");
  assert.ok(halo.at.style.includes("fill:none") && halo.at.style.includes("stroke:" + CHIP.LIT_INK), halo.at.style);
  assert.equal(+halo.at.width, CHIP.SIZE + 2 * CHIP.LIT_PAD);
  const tabbed = glyphCtx(chip({ tab: "sell", tab_at: 7 }), 7 + 2 * CHIP.LAND_S);
  const g = tabbed[0];
  const tg = g.kids[g.kids.length - 1];
  assert.equal(tg.cls, "chiptab");
  assert.deepEqual(tg.kids.map((e) => e.cls), ["chiptabbody", "chiptablab"]);
  assert.equal(tg.kids[1].textContent, "SELL");
  assert.equal(tg.at.transform, "translate(0 " + (-CHIP.SIZE / 2).toFixed(1) + ") scale(1.0000)", "centred ON the top edge, settled");
  assert.equal(tg.kids[0].tag, "rect");
  assert.equal(+tg.kids[0].at.rx, CHIP.TAB_H / 2, "a capsule: fully rounded ends");
  assert.equal(+tg.kids[0].at.y, -CHIP.TAB_H / 2, "half above the edge, half on the card");
  assert.ok(tg.kids[0].at.style.startsWith("fill:" + CHIP.TAB_INK.sell));
  assert.ok(tg.kids[1].at.style.includes("font-size:" + CHIP.TAB_TYPE + "px"));
  assert.equal(glyphCtx(chip({ tab: "sell", tab_at: 7 }), 6.9).filter((e) => e.cls === "chiptab").length, 0, "no tab before its word");
});

test("T12: absent the new keys the painter's output is today's - no halo, no check, no tab", () => {
  for (const sp of [chip(), chip({ cross_at: 9 }), chip({ state: "crossed" }), chip({ readability: "landscape-phone" })]) {
    const made = glyphCtx(sp, 9.4);
    assert.deepEqual(made.filter((e) => ["chiphalo", "chiptab", "chiptabbody", "chiptablab", "chipcheck", "chipcheckdisc", "chipcheckmark"].includes(e.cls)), []);
    assert.equal(made.filter((e) => e.cls === "sq" && e.at.style).length, 0, "the X keeps its class-only stroke");
  }
});

test("T12: a seek IS the play with every state on", () => {
  const sp = chip({ state: "lit", pulse: true, tick_at: 8, idle: "breath" });
  const forward = [], backward = [];
  for (let i = 0; i <= 300; i++) forward.push(JSON.stringify(chipStates(sp, i / 20)));
  for (let i = 300; i >= 0; i--) backward.unshift(JSON.stringify(chipStates(sp, i / 20)));
  assert.deepEqual(backward, forward);
  const bs = chip({ tab: "buy", tab_at: 6 });
  const fb = [], bb = [];
  for (let i = 0; i <= 300; i++) fb.push(JSON.stringify(chipStates(bs, i / 20)));
  for (let i = 300; i >= 0; i--) bb.unshift(JSON.stringify(chipStates(bs, i / 20)));
  assert.deepEqual(bb, fb);
  const src = chipStates.toString() + chipLitF.toString() + chipTickF.toString() + chipCheckPose.toString() + chipTabPose.toString() + chipPulseOnsets.toString();
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});
