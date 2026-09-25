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
    assert.deepEqual(p.ring, stampRing(ts), `ring at ${ts}`);
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
  assert.equal(chipPose(sp, sp.at + STAMP_ARRIVAL.SHOCK_S + 0.01).ring, null, "and never held past its life");
});

test("P70 T1: the ring's peak is the compiler's fitted ring_to, else the source's RING_TO", () => {
  const ts = (4 + 0.3) - 4, fitted = chipPose(stampForm({ arrive: "stamp", ring_to: 1.4 }), 4 + 0.3).ring;
  assert.deepEqual(fitted, stampRing(ts, { RING_TO: 1.4 }));
  assert.ok(fitted.r < stampRing(ts).r);
  assert.deepEqual(chipPose(stampForm({ arrive: "stamp" }), 4 + 0.3).ring, stampRing(ts));
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
  assert.deepEqual(mid.map((e) => e.tag), ["circle", "g", "image", "text"]);
  const [ring, g, art, lab] = mid;
  assert.equal(ring.cls, "chipstampring");
  assert.equal(ring.at.stroke, "#F2F2F2", "chalk on the ledger page");
  assert.equal(ring.at.fill, "none");
  const rg = stampRing(0.254), r0 = 0.5 * Math.hypot(260, 260 * 0.8);
  assert.equal(ring.at.r, (r0 * rg.r).toFixed(1), "the art's own PAINTED radius x the ring's multiplier");
  assert.equal(ring.at["stroke-width"], rg.width.toFixed(2));
  assert.equal(ring.at.opacity, rg.alpha.toFixed(3));
  assert.equal(ring.at.cx, "960.0");
  assert.equal(ring.at.cy, "540.0", "about the painted centre - here the square's own");
  assert.match(g.at.transform, /^translate\(960\.0 540\.\d\) rotate\(-10\.39\) scale\(1\.0000\)$/);
  assert.equal(art.cls, "chipstampart");
  assert.match(lab.at.style, /font-size:59\.08px/);
  assert.equal(lab.at.y, (130 + 28 * 59.08 / 48).toFixed(1), "the gap scales with the floor");
  const plate = paintAt(sp, sp.at + 0.254, { world: { asset_id: "plate-plain" } });
  assert.equal(plate[0].at.stroke, "#25313C", "charcoal on any other ground");
  const two = paintAt(stampForm({ arrive: "stamp", label: "NVIDIA\nCHIPS" }), 4 + 2);
  assert.equal(two.filter((e) => e.tag === "tspan")[1].at.dy, +(52 * 59.08 / 48).toFixed(2), "and the line step");
  assert.deepEqual(paintAt(sp, sp.at + 2).map((e) => e.tag), ["g", "image", "text"], "the ring is never held");
});

test("P70 T1: a stamp-form chip WITHOUT arrive paints exactly what it painted - 48 px label, no ring, no turn", () => {
  const made = paintAt(stampForm(), 4.2);
  assert.deepEqual(made.map((e) => e.tag), ["g", "image", "text"]);
  assert.doesNotMatch(made[0].at.transform, /rotate/);
  assert.match(made[2].at.style, /font-size:48px/);
  assert.equal(made[2].at.y, (130 + 28).toFixed(1));
  assert.equal(made[2].at.x, 0);
});
