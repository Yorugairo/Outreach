// P57 T17 / R26-97 - THE CALLOUT PROMOTED (the P55 T7 recipe). The promotion's proof is that every golden is
// byte-identical, so what this file pins is that the module still carries the INLINE ENGINE's numbers and
// arithmetic: the dials are the literals `paintSpecies sp.kind === "callout"` and `calloutPath` carried, and the
// geometry is the same ellipse, drawn from the same angle over the same sweep with the same seeded wobble.
// E56 (a ring's one use) is the COMPILER's (_validate_callout) - the painter carries no opinion about what it
// was pointed at, and this file checks that it does not start to.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CALLOUT, calloutPad, calloutPath, calloutDrawF, calloutLabel, paintCallout }
  from "../../scripts/species/callout.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const BAR = { x: 900, y: 300, w: 120, h: 420 };     // a bar resolves to a box ...
const POINT = { x: 1180, y: 520, w: 0, h: 0 };      // ... a datum on a line to a point
const FLAT = () => 0.5;                             // the hash at its middle: no wobble at all (j = 1)
const co = (o = {}) => Object.assign({ kind: "callout", at: 10, dur: 6 }, o);
// the ring is a CHORDED polygon, not an <ellipse>: its 29 sampled vertices ride just inside the true radii
// (under a pixel at every size the page uses), so the reaches below are read to a pixel, not to the bit.
const SAMPLED = 1;
const ease = (k) => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3);   // the engine's spEase

// ---------------------------------------------------------------- the dials, as the inline code carried them
test("every dial is the inline engine's literal, to the digit, and frozen", () => {
  assert.ok(Object.isFrozen(CALLOUT));
  assert.equal(CALLOUT.DRAW_S, 0.7, "SP.CALLOUT_DRAW");
  assert.equal(CALLOUT.RX_PAD, 22, "calloutPath's rx pad - species/ring.mjs rings the same datum at it");
  assert.equal(CALLOUT.RY_PAD, 18, "... and its ry pad");
  assert.equal(CALLOUT.SEGMENTS, 28);
  assert.equal(CALLOUT.START_A, 0.6);
  assert.equal(CALLOUT.SWEEP, 2.08);
  assert.equal(CALLOUT.JITTER, 0.12);
  assert.equal(CALLOUT.HASH_SALT, 21);
  assert.deepEqual([CALLOUT.LABEL_AT, CALLOUT.LABEL_POP_S, CALLOUT.LABEL_FROM, CALLOUT.LABEL_SPAN], [0.8, 0.25, 0.7, 0.3]);
  assert.deepEqual([CALLOUT.LABEL_DX, CALLOUT.LABEL_DY, CALLOUT.PAD_DY_K], [34, -10, 0.4]);
  assert.equal(CALLOUT.LABEL_FROM + CALLOUT.LABEL_SPAN, 1, "the pop ends at its own size, never over it");
});

test("E56 is the COMPILER's: the painter never reads what it was pointed at", () => {
  const src = paintCallout.toString() + calloutPath.toString() + calloutLabel.toString();
  assert.ok(!/target\s*\.\s*kind/.test(src), "the use is refused at build time (_validate_callout), never softened here");
});

// ---------------------------------------------------------------- the pad
test("the pad is a number or nothing", () => {
  assert.equal(calloutPad(22), 22);
  assert.equal(calloutPad("24"), 24, "the engine coerced a numeric string, and still does");
  for (const bad of [undefined, null, "", "wide", NaN, Infinity]) assert.equal(calloutPad(bad), 0, String(bad));
});

// ---------------------------------------------------------------- the ellipse
test("the ring is SEGMENTS chords round the box, at the callout's own pads", () => {
  const d = calloutPath(BAR, 7, 0, FLAT);
  const pts = d.split(" L ").join(" ").trim();
  assert.ok(d.startsWith("M"), "one move, then lines");
  assert.equal((d.match(/L/g) || []).length, CALLOUT.SEGMENTS, "28 chords - 29 points, the last closing over the first");
  assert.equal((d.match(/M/g) || []).length, 1);
  assert.ok(pts.length > 0);
  const xy = d.replace(/[ML]/g, " ").trim().split(/\s+/).map(Number);
  const xs = xy.filter((_, i) => i % 2 === 0), ys = xy.filter((_, i) => i % 2 === 1);
  const cx = BAR.x + BAR.w / 2, cy = BAR.y + BAR.h / 2;
  const rx = BAR.w / 2 + CALLOUT.RX_PAD, ry = BAR.h / 2 + CALLOUT.RY_PAD;
  assert.ok(near(Math.max(...xs), cx + rx, SAMPLED) && near(Math.min(...xs), cx - rx, SAMPLED), "the x reach is w/2 + RX_PAD");
  assert.ok(near(Math.max(...ys), cy + ry, SAMPLED) && near(Math.min(...ys), cy - ry, SAMPLED), "the y reach is h/2 + RY_PAD");
  assert.ok(xy.every((v) => /^-?\d+(\.\d)?$/.test(v.toFixed(1))), "written to one decimal");
});

test("the nib starts up and left and sweeps PAST the full turn, so the ring closes over its own start", () => {
  const d = calloutPath(POINT, 3, 0, FLAT).replace(/[ML]/g, " ").trim().split(/\s+/).map(Number);
  const rx = CALLOUT.RX_PAD, ry = CALLOUT.RY_PAD;
  const a0 = -Math.PI * CALLOUT.START_A, a1 = a0 + Math.PI * CALLOUT.SWEEP;
  assert.ok(near(d[0], +(POINT.x + Math.cos(a0) * rx).toFixed(1), 0.05), "the first point is at -0.6 PI");
  assert.ok(near(d[1], +(POINT.y + Math.sin(a0) * ry).toFixed(1), 0.05));
  assert.ok(near(d[d.length - 2], +(POINT.x + Math.cos(a1) * rx).toFixed(1), 0.05), "the last is 2.08 PI on");
  assert.ok(CALLOUT.SWEEP > 2, "past the full turn: a hand overshoots the close");
});

test("a pad widens both radii, and a bare point rings at the pads alone", () => {
  const bare = calloutPath(POINT, 5, 0, FLAT).replace(/[ML]/g, " ").trim().split(/\s+/).map(Number);
  const wide = calloutPath(POINT, 5, 40, FLAT).replace(/[ML]/g, " ").trim().split(/\s+/).map(Number);
  const reach = (v) => Math.max(...v.filter((_, i) => i % 2 === 0)) - Math.min(...v.filter((_, i) => i % 2 === 0));
  const tall = (v) => Math.max(...v.filter((_, i) => i % 2 === 1)) - Math.min(...v.filter((_, i) => i % 2 === 1));
  assert.ok(near(reach(bare), 2 * CALLOUT.RX_PAD, SAMPLED) && near(tall(bare), 2 * CALLOUT.RY_PAD, SAMPLED));
  assert.ok(near(reach(wide), reach(bare) + 80, SAMPLED), "a pad of 40 adds 40 to each side ...");
  assert.ok(near(tall(wide), tall(bare) + 80, SAMPLED), "... in both axes, the way the hand rings wider");
  assert.equal(calloutPath(POINT, 5, "40", FLAT), calloutPath(POINT, 5, 40, FLAT), "a numeric string is the same pad");
});

test("the wobble is the seeded hash's alone: bounded by JITTER, the same seed the same path", () => {
  const hash = (seed, i, salt) => ((seed + i * 11 + salt) % 100) / 100;
  const d = calloutPath(BAR, 9, 0, hash);
  assert.equal(d, calloutPath(BAR, 9, 0, hash), "a pure function: a scrubbed frame is the played frame");
  assert.notEqual(d, calloutPath(BAR, 10, 0, hash), "another scene's seed is another hand");
  const cx = BAR.x + BAR.w / 2, cy = BAR.y + BAR.h / 2;
  const rx = BAR.w / 2 + CALLOUT.RX_PAD, ry = BAR.h / 2 + CALLOUT.RY_PAD;
  const xy = d.replace(/[ML]/g, " ").trim().split(/\s+/).map(Number);
  for (let i = 0; i < xy.length; i += 2) {
    const r = Math.hypot((xy[i] - cx) / rx, (xy[i + 1] - cy) / ry);
    assert.ok(r >= 1 - CALLOUT.JITTER / 2 - 1e-3 && r <= 1 + CALLOUT.JITTER / 2 + 1e-3, `vertex ${i / 2} rides within +/- 6 %: ${r}`);
  }
  let salts = new Set();
  calloutPath(BAR, 9, 0, (s, i, salt) => { salts.add(salt); return 0.5; });
  assert.deepEqual([...salts], [CALLOUT.HASH_SALT], "one salt - the callout's own stream of the one hash");
});

// ---------------------------------------------------------------- the clocks
test("the draw runs the species' own elapsed time over DRAW_S", () => {
  assert.equal(calloutDrawF(0, 6), 0);
  assert.ok(near(calloutDrawF(CALLOUT.DRAW_S / 6, 6), 1), "closed exactly at DRAW_S ...");
  assert.ok(calloutDrawF(0.5, 6) > 1, "... and drawOn clamps it after, as it always did");
  assert.ok(near(calloutDrawF(0.1, 7) / calloutDrawF(0.05, 7), 2), "linear in the elapsed time");
});

test("the label waits 0.8 of the draw, then pops 0.7 -> 1.0 over LABEL_POP_S", () => {
  const at = CALLOUT.DRAW_S * CALLOUT.LABEL_AT;          // 0.56 s in
  const k = (s) => s / 6;                                 // dur = 6
  assert.equal(calloutLabel(BAR, 0, k(at - 0.01), 6, undefined, ease).shown, false);
  assert.equal(calloutLabel(BAR, 0, k(at + 0.01), 6, undefined, ease).shown, true);
  assert.ok(near(calloutLabel(BAR, 0, k(at), 6, undefined, ease).scale, CALLOUT.LABEL_FROM), "it pops FROM 0.7, never from nothing");
  assert.ok(near(calloutLabel(BAR, 0, k(at + CALLOUT.LABEL_POP_S), 6, undefined, ease).scale, 1), "and lands at its own size");
  const mid = calloutLabel(BAR, 0, k(at + 0.1), 6, undefined, ease).scale;
  assert.ok(mid > CALLOUT.LABEL_FROM && mid < 1);
});

test("the label is written off the box's right edge and above its top, and a pad pushes it out and up", () => {
  const L = calloutLabel(BAR, 0, 1, 6, undefined, ease);
  assert.equal(L.x, BAR.x + BAR.w + CALLOUT.LABEL_DX);
  assert.equal(L.y, BAR.y + CALLOUT.LABEL_DY);
  assert.ok(L.y < BAR.y, "above the top edge: never over the number it rings");
  const P = calloutLabel(BAR, 40, 1, 6, undefined, ease);
  assert.equal(P.x, L.x + 40, "the pad pushes the label out with the ring ...");
  assert.equal(P.y, L.y - 40 * CALLOUT.PAD_DY_K, "... and lifts it by PAD_DY_K of the pad");
});

test("label_scale is opt-in and multiplies the pop (a stamp on a plate reads at phone size)", () => {
  const plain = calloutLabel(BAR, 0, 1, 6, undefined, ease).scale;
  assert.equal(calloutLabel(BAR, 0, 1, 6, 2.2, ease).scale, plain * 2.2);
  assert.equal(calloutLabel(BAR, 0, 1, 6, "2.2", ease).scale, plain * 2.2, "the engine coerced a numeric string");
  for (const bad of [undefined, null, 0, -1, NaN, "big"]) assert.equal(calloutLabel(BAR, 0, 1, 6, bad, ease).scale, plain, String(bad));
});

// ---------------------------------------------------------------- the painter, on a stub surface
function stub(sp, k, opts = {}) {
  const made = [], drawn = [];
  const el = (tag, cls, parent, at) => {
    const e = { tag, cls, at: Object.assign({}, at), kids: [], textContent: "",
                setAttribute(x, v) { this.at[x] = v; }, getAttribute(x) { return this.at[x]; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e;
  };
  paintCallout({ sp, k, dur: sp.dur, t: sp.at + k * sp.dur, svg: { kids: [] }, el,
                 resolveTarget: () => (opts.noTarget ? null : Object.assign({}, opts.box || BAR)),
                 drawOn: (p, f) => { drawn.push(f); p.setAttribute("stroke-dashoffset", f.toFixed(3)); },
                 ease, hash: FLAT, seed: 7, si: 0,
                 squigglePath: (b) => `M${b.x} ${b.y + b.h} L${b.x + b.w} ${b.y + b.h}`,
                 SQUIG_DRAW: 0.45, STAGE_W: 1920, STAGE_H: 1080 });
  return { made, drawn };
}

test("the targeting law: no resolved target, nothing painted", () => {
  assert.equal(stub(co({ label: "25%" }), 0.5, { noTarget: true }).made.length, 0);
});

test("the ring draws as a .co path on the module's own clock, with the label after it", () => {
  const early = stub(co({ label: "25%" }), 0.02);      // 0.12 s in: the hand has started, the label has not
  assert.equal(early.made.filter((e) => e.cls === "co").length, 1);
  assert.ok(near(early.drawn[0], calloutDrawF(0.02, 6)), "the draw fraction is the module's, handed to drawOn raw");
  assert.equal(early.made.filter((e) => e.cls === "lab").length, 0, "the label waits for 0.8 of the draw");
  const late = stub(co({ label: "25%", label_scale: 2.2 }), 0.2);
  const lab = late.made.find((e) => e.cls === "lab");
  assert.equal(lab.textContent, "25%");
  assert.equal(lab.at.x, (BAR.x + BAR.w + CALLOUT.LABEL_DX).toFixed(1));
  assert.ok(/^translate\(.*\) scale\(\d\.\d{3}\) translate\(.*\)$/.test(lab.at.transform), "scaled about its own anchor");
  assert.equal(stub(co(), 0.9).made.filter((e) => e.cls === "lab").length, 0, "no label declared, none written");
});

test('form: "underline" is the SQUIGGLE\'s stroke and clock, not the ring (P50 T3, E56\'s one exception)', () => {
  const u = stub(co({ form: "underline", label: "the quote" }), 0.05);
  assert.equal(u.made.length, 1, "one stroke, and no label: an underline is not a ring");
  assert.equal(u.made[0].cls, "sq");
  assert.equal(u.made[0].at.d, `M${BAR.x} ${BAR.y + BAR.h} L${BAR.x + BAR.w} ${BAR.y + BAR.h}`, "the squiggle's own path, under the phrase");
  assert.ok(u.drawn[0] > 0.05 * 6 / 0.45 * 0.5, "on underlineFrac over SQUIG_DRAW: the hand runs out fast");
  assert.ok(u.drawn[0] <= 1);
});
