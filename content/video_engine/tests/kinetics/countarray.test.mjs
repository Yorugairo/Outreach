// P52 T7 - THE ISOMETRIC COUNT ARRAY (EXPLORATION-REVIEW-2026-09-10.md:59, the reference at 7:43). The field's
// whole visual state is a pure function of t, sp.at and sp.count: a 2:1 rhombus lattice with NO perspective cheat,
// icons arriving in READING ORDER on the chip's two-spring landing, the count written as the claim, and nothing
// spinning at any t. These tests pin all four, and pin that nothing is remembered between calls.
import { test } from "node:test";
import assert from "node:assert/strict";
import { SPRING, springPop } from "../../scripts/kinetics/spring.mjs";
import { CHIP, chipLand } from "../../scripts/species/chip.mjs";
import { COUNT, countCells, countLayout, countArriveAt, countCellPose, countClaimF, countPose,
         countTilePath, countSpring, paintCountArray } from "../../scripts/species/countarray.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const BOX = { x: 120, y: 420, w: 900, h: 560 };
const field = (o = {}) => Object.assign({ kind: "count_array", at: 5, dur: 12, count: 6, icon: "factory",
                                          claim: "SIX PLANTS", target: { kind: "region", x0: 0.06, y0: 0.39, x1: 0.53, y1: 0.9 } }, o);

// ---------------------------------------------------------------- the dials
test("the dials are the field's, and every clock is a real window", () => {
  assert.ok(COUNT.MIN >= 2, "a count of one is a chip, not a field");
  assert.ok(COUNT.MAX <= 12, "past a dozen the number is read, not the field");
  assert.ok(COUNT.LAND_S > 0 && COUNT.STEP > 0 && COUNT.CLAIM_S > 0 && COUNT.FADE_S > 0);
  assert.ok(COUNT.POP_FROM > 0 && COUNT.POP_FROM < 1, "an icon springs UP to its size, never from nothing");
  assert.equal(COUNT.RISE, 0.5, "0.5 IS the 2:1 rhombus - the dimetric step");
  assert.ok(COUNT.ICON < CHIP.SIZE, "an icon in a field is smaller than a chip's card");
});

// ---------------------------------------------------------------- the lattice: 2:1, and no perspective cheat
test("the lattice is a 2:1 rhombus: x = (c - r) * PITCH, y = (c + r) * PITCH / 2, and nothing else", () => {
  const lay = countLayout({ x: 0, y: 0, w: 0, h: 0 }, 9);   // no box: k = 1, so the raw lattice is readable
  assert.equal(lay.k, 1);
  for (const cell of lay.cells) {
    assert.ok(near(cell.x, (cell.c - cell.r) * COUNT.PITCH), `x of (${cell.c},${cell.r})`);
    assert.ok(near(cell.y, (cell.c + cell.r) * COUNT.PITCH * 0.5), `y of (${cell.c},${cell.r})`);
  }
  // the two basis vectors of the lattice, measured off the cells themselves: one step across is twice one step down
  const at = (c, r) => lay.cells.find((p) => p.c === c && p.r === r);
  const u = [at(1, 0).x - at(0, 0).x, at(1, 0).y - at(0, 0).y];
  const v = [at(0, 1).x - at(0, 0).x, at(0, 1).y - at(0, 0).y];
  assert.ok(near(Math.abs(u[0] / u[1]), 2) && near(Math.abs(v[0] / v[1]), 2), `${u} ${v} - a 2:1 rhombus, both ways`);
  assert.ok(near(Math.hypot(...u), Math.hypot(...v)), "the two axes are the SAME length on the page: isometric, not oblique");
});

test("NO PERSPECTIVE CHEAT: one scale for every cell, whatever the box, and depth changes nothing but y", () => {
  for (const box of [{ x: 0, y: 0, w: 400, h: 300 }, BOX, { x: 10, y: 10, w: 1900, h: 1000 }]) {
    const lay = countLayout(box, 6);
    assert.ok(lay.k >= COUNT.MIN_K && lay.k <= 1, `k ${lay.k}`);
    const rows = new Map();
    lay.cells.forEach((c) => rows.set(c.r, (rows.get(c.r) || []).concat([c])));
    const steps = [...rows.values()].map((cs) => cs[1] && cs[1].sx - cs[0].sx).filter((v) => v !== undefined);
    for (const s of steps) assert.ok(near(s, steps[0], 1e-9), "a row further back is NOT drawn narrower - no foreshortening");
  }
});

test("the icons are all one size at rest: the pose is the same for every cell once it has landed", () => {
  const sp = field({ count: 9 });
  const t = countArriveAt(sp, 8) + COUNT.LAND_S + 2;
  const pose = countPose(sp, t);
  for (const c of pose.cells) assert.deepEqual([c.scale, c.dy, c.fade], [1, 0, 1]);
  assert.equal(pose.landed, 9);
});

// ---------------------------------------------------------------- reading order, one icon per word
test("the cells are in READING ORDER - a row's columns, then the next row", () => {
  assert.deepEqual(countCells(6).map((c) => [c.c, c.r]), [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]]);
  assert.deepEqual(countCells(4).map((c) => [c.c, c.r]), [[0, 0], [1, 0], [0, 1], [1, 1]]);
  assert.deepEqual(countCells(3).map((c) => [c.c, c.r]), [[0, 0], [1, 0], [0, 1]], "the last row may be partial");
  assert.equal(countCells(9).length, 9);
  assert.equal(countCells(99).length, COUNT.MAX, "the bound holds in the layout too, not only in the compiler");
});

test("one icon per word: arrival i is STEP after i - 1, and the row's own step wins", () => {
  const sp = field();
  for (let i = 0; i < 6; i++) assert.ok(near(countArriveAt(sp, i), 5 + i * COUNT.STEP));
  const slow = field({ step: 0.5 });
  for (let i = 0; i < 6; i++) assert.ok(near(countArriveAt(slow, i), 5 + i * 0.5));
  const t = countArriveAt(sp, 2) + 0.01;   // mid-field: three have started, the fourth has not
  const pose = countPose(sp, t);
  assert.ok(pose.cells[2].fade > 0 && pose.cells[3].fade === 0, "the field fills in order, never all at once");
  for (let i = 1; i < 6; i++) assert.ok(pose.cells[i - 1].u >= pose.cells[i].u, "no icon overtakes the one before it");
});

// ---------------------------------------------------------------- the landing IS the chip's
test("an icon lands on the CHIP's two-spring law, under the field's own dials", () => {
  const sp = field();
  for (let i = 0; i <= 40; i++) {
    const u = i / 40, t = countArriveAt(sp, 3) + u * COUNT.LAND_S;
    const pose = countCellPose(sp, t, 3);
    assert.ok(near(pose.scale, COUNT.POP_FROM + (1 - COUNT.POP_FROM) * springPop(u)), `u=${u}`);
    assert.ok(near(pose.scale, countSpring(u)), "countSpring is that same law, written once");
    assert.ok(near(pose.scale, chipLand(t, countArriveAt(sp, 3), COUNT).scale, 1e-12), "and it IS chipLand");
  }
  let max = 0;
  for (let i = 0; i <= 2000; i++) max = Math.max(max, countSpring(i / 2000));
  assert.ok(near(max, 1 + (1 - COUNT.POP_FROM) * SPRING.MP, 1e-4), `the POP preset's overshoot: ${max}`);
  const before = countCellPose(sp, 0, 0);
  assert.deepEqual([before.u, before.fade, before.dy], [0, 0, -COUNT.DROP_PX]);
});

// ---------------------------------------------------------------- the count IS the claim
test("the claim is written once the LAST icon has landed, and never before", () => {
  const sp = field();
  const last = countArriveAt(sp, 5) + COUNT.LAND_S;
  assert.equal(countClaimF(sp, last), 0);
  assert.equal(countClaimF(sp, last + COUNT.CLAIM_LAG), 0);
  assert.ok(near(countClaimF(sp, last + COUNT.CLAIM_LAG + COUNT.CLAIM_S / 2), 0.5));
  assert.equal(countClaimF(sp, last + COUNT.CLAIM_LAG + COUNT.CLAIM_S), 1);
  assert.equal(countClaimF(sp, last + 30), 1);
  assert.ok(countClaimF(field({ count: 3 }), last) > 0, "a shorter field says its number sooner");
});

// ---------------------------------------------------------------- the tile
test("the tile under an icon is the lattice's own 2:1 rhombus, drawn about the cell's centre", () => {
  const d = countTilePath(1), nums = d.match(/-?\d+(\.\d+)?/g).map(Number);
  const a = COUNT.PITCH * COUNT.TILE_K;
  assert.equal(d.startsWith("M0 "), true);
  assert.ok(d.endsWith("Z"), "a tile is closed - it is a plate, not a path");
  assert.ok(nums.includes(a) || nums.includes(+a.toFixed(1)), d);
  assert.ok(Math.max(...nums.map(Math.abs)) / Math.min(...nums.filter((v) => v !== 0).map(Math.abs)) === 2, "2:1, like the lattice");
});

// ---------------------------------------------------------------- pure function of t
test("a seek IS the play: the same t gives the same bits, in any order, with nothing remembered", () => {
  const sp = field({ idle: "breath" });
  const forward = [], backward = [];
  for (let i = 0; i <= 400; i++) forward.push(JSON.stringify(countPose(sp, i / 20)));
  for (let i = 400; i >= 0; i--) backward.unshift(JSON.stringify(countPose(sp, i / 20)));
  assert.deepEqual(backward, forward);
  assert.equal(JSON.stringify(countPose(sp, 8.15)), forward[163]);
});

test("nothing in the module reaches for a clock or a random", () => {
  const src = paintCountArray.toString() + countPose.toString() + countLayout.toString() + countClaimF.toString();
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});

// ---------------------------------------------------------------- the painter, on a stub surface
const GEO = JSON.stringify({ vb: [0, 0, 24, 24], el: [{ t: "path", a: { d: "M12 16h.01" } }] });

function stub(sp, t, opts = {}) {
  const made = [];
  const el = (tag, cls, parent, at) => {
    const e = { tag, cls, at: Object.assign({}, at), kids: [], textContent: "",
                setAttribute(k, v) { this.at[k] = v; }, getAttribute(k) { return this.at[k]; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e;
  };
  const idles = [];
  const ctx = { sp, t, svg: { kids: [] }, el, A: { "icon:factory": GEO },
                resolveTarget: () => (opts.noTarget ? null : { x: BOX.x, y: BOX.y, w: BOX.w, h: BOX.h }),
                ease: (k) => 1 - Math.pow(1 - Math.min(1, Math.max(0, k)), 3),
                hash: (a, b, c) => ((a + b * 7 + c) % 100) / 100, seed: 3, si: 1,
                idle: (kind, tt, ph) => { idles.push([kind, ph]); return { scale: 1, dx: 0, dy: 0 }; },
                drawOn: (p, k) => p.setAttribute("stroke-dashoffset", k.toFixed(3)), STAGE_W: 1920, STAGE_H: 1080 };
  paintCountArray(ctx);
  return { made, idles };
}

test("the painter draws nothing when the target does not resolve", () => {
  assert.equal(stub(field(), 9, { noTarget: true }).made.length, 0, "the targeting law: no resolved target, nothing painted");
});

test("the painter draws one tile and one glyph per LANDED icon, and the claim last", () => {
  const sp = field();
  const early = stub(sp, countArriveAt(sp, 1) + 0.05);
  assert.equal(early.made.filter((e) => e.cls === "catile").length, 2, "two icons are on the field, not six");
  assert.equal(early.made.filter((e) => e.cls === "caclaim").length, 0, "the claim waits for the last icon");
  const done = stub(sp, countArriveAt(sp, 5) + 2);
  assert.equal(done.made.filter((e) => e.cls === "catile").length, 6);
  assert.equal(done.made.filter((e) => e.cls === "caglyph").length, 6, "one SOURCED glyph each - identical icons");
  const claim = done.made.find((e) => e.cls === "caclaim");
  assert.equal(claim.textContent, "SIX PLANTS");
  assert.ok(+claim.at.opacity === 1);
});

test("NOTHING SPINS: no attribute the painter writes carries a rotation, at any t", () => {
  const sp = field();
  for (const t of [4.9, 5.0, 5.2, 6.1, 7.4, 9.0, 14.0]) {
    for (const e of stub(sp, t).made) {
      for (const [k, v] of Object.entries(e.at)) {
        assert.ok(!/rotate|skew|matrix/.test(String(v)), `${t}: ${e.tag}.${k} = ${v}`);
      }
    }
  }
});

test("the field's idle is NAMED, phased per cell, and 'none' is declared stillness", () => {
  const sp = field();
  const dflt = stub(sp, 9);
  assert.deepEqual([...new Set(dflt.idles.map((i) => i[0]))], ["breath"], "unnamed = the field's own class default");
  assert.equal(new Set(dflt.idles.map((i) => i[1])).size, dflt.idles.length, "no two icons breathe in step (E49)");
  assert.deepEqual([...new Set(stub(field({ idle: "drift" }), 9).idles.map((i) => i[0]))], ["drift"]);
  assert.equal(stub(field({ idle: "none" }), 9).idles.length, 0, "declared stillness asks the idle for nothing");
});

test("a glyph the asset map does not carry leaves the field standing, and draws no geometry", () => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: Object.assign({}, at), kids: [], textContent: "", setAttribute() {} };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  paintCountArray({ sp: field({ icon: "nope" }), t: 12, svg: { kids: [] }, el, A: {},
                    resolveTarget: () => ({ x: 0, y: 0, w: 900, h: 600 }), ease: (k) => k,
                    hash: () => 0.5, idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0,
                    drawOn: () => {}, STAGE_W: 1920, STAGE_H: 1080 });
  assert.equal(made.filter((e) => e.cls === "catile").length, 6);
  assert.equal(made.filter((e) => e.cls === "caglyph").length, 0, "no glyph is invented when none was sourced");
});
