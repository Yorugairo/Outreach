// P55 T7 - THE VERDICT STACK, promoted from the engine's inline drawStack with every frame byte-identical. The pose
// is a pure function of t: enter from depth on the word beat, focus while the phrase is spoken, recede to a rail spot
// when the next beat lands, burst radially on clear_at. These tests pin the clocks, the blend, the bearing and the stagger.
import { test } from "node:test";
import assert from "node:assert/strict";
import { VERDICT, verdictGeometry, verdictNextAt, verdictPose, verdictBurst, paintVerdict } from "../../scripts/species/verdict.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const W = 1920, H = 1080;
const items = (ats) => ats.map((at, i) => Object.assign({ at }, verdictGeometry(i, W, H)));

test("the dials carry the inline code's values, frozen", () => {
  assert.ok(Object.isFrozen(VERDICT) && Object.isFrozen(VERDICT.SPOTS) && Object.isFrozen(VERDICT.SPOTS[0]));
  assert.equal(VERDICT.ENTER_Z, -700, "the code's depth; doc 29 s9.24's -940 is stale");
  assert.equal(VERDICT.SPOTS.length, 9);
  assert.deepEqual([VERDICT.ENTER_S, VERDICT.RECEDE_S, VERDICT.LAST_RECEDE_LEAD, VERDICT.ENTER_SWING, VERDICT.ENTER_ROT_Y],
                   [0.9, 1.0, 0.9, 460, 30]);
  assert.deepEqual([VERDICT.BURST_X, VERDICT.BURST_Y, VERDICT.BURST_Z, VERDICT.BURST_SPIN, VERDICT.BURST_SCALE, VERDICT.BURST_STAGGER, VERDICT.BURST_S],
                   [560, 420, 340, 24, 0.22, 0.06, 0.5]);
  assert.deepEqual([VERDICT.ACTIVE_X, VERDICT.ACTIVE_DX, VERDICT.ACTIVE_Y, VERDICT.ACTIVE_ROW_DY, VERDICT.ACTIVE_W], [930, 70, 400, 26, 840]);
  assert.equal(VERDICT.REMOVE_AFTER, 1.4);
});

test("the geometry: rail spot, alternating focus side, landscape-normalised bearing", () => {
  const g0 = verdictGeometry(0, W, H), g1 = verdictGeometry(1, W, H);
  assert.deepEqual([g0.L, g0.T, g0.W], [2, 5, 24]);
  assert.equal(g0.dir, -1); assert.equal(g1.dir, 1);
  assert.equal(g0.tilt, -3); assert.equal(verdictGeometry(6, W, H).tilt, -3, "tilts cycle over six");
  const wpx = 24 / 100 * W;
  assert.ok(near(g0.asc, 840 / wpx));
  assert.ok(near(g0.adx, (930 - 70) - (2 / 100 * W + wpx / 2)));
  assert.deepEqual([verdictGeometry(9, W, H).L, verdictGeometry(9, W, H).T], [2, 5], "spots cycle over nine");
});

test("the enter clock: opacity 0 before the beat, 1 once ENTER_S has run", () => {
  const it = items([3])[0];
  assert.equal(verdictPose(it, 0, 2.5, 99, 100).opacity, 0);
  assert.equal(verdictPose(it, 0, 3, 99, 100).opacity, 0);
  assert.ok(near(verdictPose(it, 0, 3 + 0.9, 99, 100).opacity, 1, 1e-12));
  assert.equal(verdictPose(it, 0, 3.95, 99, 100).opacity, 1);
  const deep = verdictPose(it, 0, 3, 99, 100);
  assert.equal(deep.tz, -700); assert.equal(deep.rotY, 30 * it.dir);
  assert.ok(verdictPose(it, 0, 5, 99, 100).tz === 0, "landed: no depth left (-0, printed \"0\" as the inline code did)");
});

test("the focus hand-off: a = 1 between beats, 0 once the next beat + RECEDE_S has passed", () => {
  const its = items([3, 5, 7]);
  const next = verdictNextAt(its, 0, 20);
  assert.equal(next, 5);
  assert.equal(verdictPose(its[0], 0, 4.5, next, 20).a, 1);
  assert.equal(verdictPose(its[0], 0, 4.5, next, 20).z, 9);
  assert.ok(near(verdictPose(its[0], 0, 5.5, next, 20).a, 0.5), "the in-out cubic is half way at half RECEDE_S");
  assert.equal(verdictPose(its[0], 0, 6.0, next, 20).a, 0);
  assert.equal(verdictPose(its[0], 0, 6.5, next, 20).z, 7);
  assert.ok(near(verdictNextAt(its, 2, 20), 20 - 0.9), "the last card recedes LAST_RECEDE_LEAD before the clear");
});

test("the burst bearing: a card right of centre moves right, a card left of centre moves left", () => {
  const right = verdictGeometry(3, W, H), left = verdictGeometry(0, W, H);   // spots at 74 % and 2 %
  assert.ok(right.bx > 0 && left.bx < 0);
  const at = 20.25;
  assert.ok(verdictBurst(Object.assign({ at: 0 }, right), 3, at + 0.18, 20).tx > 0);
  assert.ok(verdictBurst(Object.assign({ at: 0 }, left), 0, at, 20).tx < 0);
  const low = verdictGeometry(7, W, H);
  assert.ok(low.by > 0 && verdictBurst(Object.assign({ at: 0 }, low), 7, 21, 20).ty > 0, "a low card falls");
});

test("the stagger: card i starts BURST_STAGGER after card i-1, each over BURST_S", () => {
  const its = items([3, 5, 7, 9]);
  for (let i = 0; i < its.length; i++) {
    assert.equal(verdictBurst(its[i], i, 20 + i * 0.06 - 1e-9, 20).cb, 0, `card ${i} still before its start`);
    assert.ok(verdictBurst(its[i], i, 20 + i * 0.06 + 0.01, 20).cb > 0, `card ${i} has started`);
  }
  for (let i = 1; i < its.length; i++)
    assert.ok(near(verdictBurst(its[i], i, 20.3 + 0.06, 20).cb, verdictBurst(its[i - 1], i - 1, 20.3, 20).cb, 1e-9));
  const done = verdictBurst(its[0], 0, 20.5, 20);
  assert.deepEqual([done.cb, done.opacity, done.tz, done.scale], [1, 0, 340, 1.22]);
});

test("a seek IS the play: the same t gives the same bits in any order", () => {
  const its = items([3, 5, 7]);
  const at = (t) => JSON.stringify(its.map((it, i) => t >= 20 ? verdictBurst(it, i, t, 20) : verdictPose(it, i, t, verdictNextAt(its, i, 20), 20)));
  const fwd = []; for (let k = 0; k <= 220; k++) fwd.push(at(k / 10));
  const back = []; for (let k = 220; k >= 0; k--) back.unshift(at(k / 10));
  assert.deepEqual(back, fwd);
  const src = paintVerdict.toString() + verdictPose.toString() + verdictBurst.toString();
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src));
});

test("the painter writes the inline strings and removes the stack outside its life", () => {
  const card = () => ({ style: {} });
  const its = items([3, 5]).map((it) => Object.assign(it, { card: card() }));
  let removed = 0;
  const st = { sb: { remove: () => removed++ }, items: its, clear_at: 10 };
  assert.equal(paintVerdict(st, 4.5, { enter: 2 }), true);
  const p = verdictPose(its[0], 0, 4.5, 5, 10);
  assert.equal(its[0].card.style.transform,
    `translate(${p.tx.toFixed(1)}px, ${p.ty.toFixed(1)}px) translateZ(${p.tz}px) rotateY(${p.rotY}deg) rotate(${p.rot.toFixed(2)}deg) scale(${p.scale.toFixed(3)})`);
  assert.equal(its[0].card.style.zIndex, 9);
  assert.equal(paintVerdict(st, 10.2, { enter: 2 }), true);
  assert.match(its[1].card.style.transform, /^translate\([-\d.e]+px, [-\d.e]+px\) translateZ\([\d.e-]+px\) rotate\([-\d.e]+deg\) scale\([\d.e-]+\)$/);
  assert.equal(removed, 0);
  assert.equal(paintVerdict(st, 10 + 1.41, { enter: 2 }), false);
  assert.equal(paintVerdict(st, 1.4, { enter: 2 }), false);
  assert.equal(removed, 2);
});
