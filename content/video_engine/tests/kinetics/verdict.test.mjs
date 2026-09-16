// P55 T7 - THE VERDICT STACK, promoted from the engine's inline drawStack with every frame byte-identical. The pose
// is a pure function of t: enter from depth on the word beat, focus while the phrase is spoken, recede to a rail spot
// when the next beat lands, burst radially on clear_at. These tests pin the clocks, the blend, the bearing and the stagger.
import { test } from "node:test";
import assert from "node:assert/strict";
import { VERDICT, VERDICT_9X16, verdictGeometry, verdictFocusRect, verdictGatherXf, verdictGather,
         verdictNextAt, verdictPose, verdictBurst, paintVerdict } from "../../scripts/species/verdict.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const W = 1920, H = 1080;
const items = (ats) => ats.map((at, i) => Object.assign({ at }, verdictGeometry(i, W, H)));

test("the dials carry the inline code's values, frozen", () => {
  assert.ok(Object.isFrozen(VERDICT) && Object.isFrozen(VERDICT.SPOTS) && Object.isFrozen(VERDICT.SPOTS[0]));
  assert.equal(VERDICT.ENTER_Z, -700, "the code's depth; doc 29 s9.24's -940 is stale");
  assert.equal(VERDICT.SPOTS.length, 9);
  assert.deepEqual([VERDICT.ENTER_S, VERDICT.RECEDE_S, VERDICT.LAST_RECEDE_LEAD, VERDICT.ENTER_SWING, VERDICT.ENTER_ROT_Y],
                   [0.9, 1.0, 0.9, 460, 30]);
  /* P61 T7d / E99 s61 - THE FULL FRAME KEEPS THE REFERENCE ("on horizontal i still prefer the reference"):
     Steel and Paper's own measured burst, 0.06 apart over 0.50 s from the rails, and no gather at all. */
  assert.equal(VERDICT.GATHER, false);
  assert.deepEqual([VERDICT.BURST_X, VERDICT.BURST_Y, VERDICT.BURST_Z, VERDICT.BURST_SPIN, VERDICT.BURST_SCALE, VERDICT.BURST_STAGGER, VERDICT.BURST_S],
                   [560, 420, 340, 24, 0.22, 0.06, 0.5]);
  assert.deepEqual([VERDICT.GATHER_LEAD, VERDICT.GATHER_PULL, VERDICT.GATHER_CORE, VERDICT.GATHER_GAP, VERDICT.BURST_CENTRE_BY],
                   [undefined, undefined, undefined, undefined, undefined],
                   "the gather's dials are the SHORT's, not the full frame's (E99 s61)");
  /* ... and they all live on VERDICT_9X16, with T7c's values (E99 s59, kept by s61: "that vertical is great") */
  assert.equal(VERDICT_9X16.GATHER, true);
  assert.deepEqual([VERDICT_9X16.GATHER_LEAD, VERDICT_9X16.GATHER_PULL, VERDICT_9X16.GATHER_CORE,
                    VERDICT_9X16.GATHER_GAP, VERDICT_9X16.BURST_CENTRE_BY], [0.9, 0.22, 0.5, 16, 1.0]);
  assert.deepEqual([VERDICT_9X16.BURST_STAGGER, VERDICT_9X16.BURST_S], [0.035, 0.42]);
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
  /* P61 T7d / E99 s61 - THE FULL FRAME: the last card DOES hand the focus on, LAST_RECEDE_LEAD before the clear,
     and is back on its raster spot when the burst fires. That is the reference's own beat, which this form keeps. */
  assert.ok(near(verdictNextAt(its, 2, 20), 20 - VERDICT.LAST_RECEDE_LEAD),
            "the full frame's last card hands the focus on 0.9 s before the clear (E99 s61)");
  const lastIt = Object.assign({ at: 7 }, verdictGeometry(2, W, H, VERDICT, 3));
  assert.equal(verdictPose(lastIt, 2, 19.05, verdictNextAt(its, 2, 20), 20).a, 1, "still at the centre as it opens");
  assert.ok(verdictPose(lastIt, 2, 20, verdictNextAt(its, 2, 20), 20).a < 0.01,
            "the last proof has RECEDED to its raster spot by the clear - no centre landing on the full frame");
  assert.deepEqual([lastIt.gx, lastIt.gy, lastIt.last], [0, 0, false], "and nothing on this form gathers");
  /* ... while the SHORT's form keeps T7c: the wall ENDS on the last proof, large at the centre (E99 s59) */
  const its9 = [3, 5, 7].map((at, i) => Object.assign({ at }, verdictGeometry(i, 1080, 1920, VERDICT_9X16, 3)));
  assert.equal(verdictNextAt(its9, 2, 20, VERDICT_9X16), 20,
               "on the SHORT the last card never hands the focus on (E99 s59): the wall ends on it");
  assert.equal(verdictPose(its9[2], 2, 19.99, verdictNextAt(its9, 2, 20, VERDICT_9X16), 20, VERDICT_9X16).a, 1,
               "the last proof is still at the centre, full size, one frame before the clear");
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
  const S = VERDICT.BURST_STAGGER;
  for (let i = 0; i < its.length; i++) {
    assert.equal(verdictBurst(its[i], i, 20 + i * S - 1e-9, 20).cb, 0, `card ${i} still before its start`);
    assert.ok(verdictBurst(its[i], i, 20 + i * S + 0.01, 20).cb > 0, `card ${i} has started`);
  }
  for (let i = 1; i < its.length; i++)
    assert.ok(near(verdictBurst(its[i], i, 20.3 + S, 20).cb, verdictBurst(its[i - 1], i - 1, 20.3, 20).cb, 1e-9));
  const done = verdictBurst(its[0], 0, 20.5, 20);
  assert.deepEqual([done.cb, done.opacity, done.tz, done.scale], [1, 0, 340, 1.22]);
});

/* P61 T7c / E99 s59 - THE GATHER, and P61 T7d / E99 s61 - IT IS THE SHORT'S FORM ONLY. The operator with the two
   clips and the reference side by side: *"that vertical is great. on horizontal i still prefer the reference."* */
const W9 = 1080, H9 = 1920, V9 = VERDICT_9X16;

test("the gather on the SHORT's form: the clock, the pull, the guard, and a wall that only ever closes", () => {
  assert.equal(verdictGather(20 - 0.9 - 1e-9, 20, V9), 0, "nothing gathers before its window");
  assert.equal(verdictGather(20, 20, V9), 1, "the gather is home exactly at the clear");
  assert.ok(near(verdictGather(20 - 0.9 / 2, 20, V9), 1 - Math.pow(0.5, 3)), "out-cubic: the reference's arrival law");
  assert.ok(verdictGather(20 - 0.9 + 0.09, 20, V9) > 0.25, "it moves at once - a wall that dawdles reads as drift");

  const n = 9, ats = [2, 3.5, 5, 6.4, 7.8, 9.2, 10.6, 12.2, 13.8];
  const its = ats.map((at, i) => Object.assign({ at }, verdictGeometry(i, W9, H9, V9, n)));
  const f = verdictFocusRect(n - 1, V9);
  assert.deepEqual([its[n - 1].gx, its[n - 1].gy], [0, 0], "the centre card does not gather toward itself");
  assert.deepEqual([its[n - 1].bx, its[n - 1].by], [0, V9.BURST_CENTRE_BY], "and it has no outward bearing");
  for (let i = 0; i < n - 1; i++) {
    const g = verdictGeometry(i, W9, H9, V9, n);
    const wpx = g.W / 100 * W9;
    const cx = g.L / 100 * W9 + wpx / 2;
    const cy = g.T / 100 * H9 + wpx * V9.CARD_H / V9.CARD_W / 2;
    const d0 = Math.hypot(f.cx - cx, f.cy - cy), d1 = Math.hypot(f.cx - cx - g.gx, f.cy - cy - g.gy);
    assert.ok(d1 < d0, `rail ${i + 1} does not draw IN`);
    assert.ok(d0 - d1 >= 60, `rail ${i + 1} draws in ${(d0 - d1).toFixed(1)}px - that is a drift, not a gather`);
    assert.ok(d0 - d1 <= V9.GATHER_PULL * d0 + 1e-9, `rail ${i + 1} draws past GATHER_PULL`);
  }
  // the guard: a rail sitting ON the centre card's core cannot move at all
  assert.deepEqual(verdictGatherXf(f.cx, f.cy, 200, 90, f, V9), { gx: 0, gy: 0 });

  // the pose: every railed card's distance to the centre card falls, frame by frame, across the whole window
  for (let i = 0; i < n - 1; i++) {
    const g = verdictGeometry(i, W9, H9, V9, n);
    const wpx = g.W / 100 * W9;
    const cx = g.L / 100 * W9 + wpx / 2, cy = g.T / 100 * H9 + wpx * V9.CARD_H / V9.CARD_W / 2;
    let prev = Infinity;
    for (let k = 0; k <= 27; k++) {
      const t = 20 - 0.9 + k / 30;
      const p = verdictPose(its[i], i, t, verdictNextAt(its, i, 20, V9), 20, V9);
      const d = Math.hypot(f.cx - (cx + p.tx), f.cy - (cy + p.ty));   // to the CENTRE card, the thing it gathers around
      assert.ok(d < prev + 1e-9, `rail ${i + 1} backs away at t ${t.toFixed(3)} (${d.toFixed(2)} > ${prev.toFixed(2)})`);
      prev = d;
    }
  }

  // the burst LEAVES the gathered wall: its first frame is the pose's last, to the pixel
  const rest = verdictPose(its[0], 0, 20, verdictNextAt(its, 0, 20, V9), 20, V9);
  const b0 = verdictBurst(its[0], 0, 20, 20, V9, rest);
  assert.ok(near(b0.tx, rest.tx) && near(b0.ty, rest.ty), "the throw starts where the gather ended - no snap back");
  assert.ok(near(b0.scale, rest.scale) && near(b0.rot, rest.rot));
  const g9 = verdictGeometry(0, W9, H9, V9, 9);
  assert.ok(Math.hypot(g9.gx, g9.gy) > 60, "the short's wall gathers");
});

/* P61 T7d / E99 s61 - and the FULL FRAME does not gather at all: the phase is OFF, not tuned down. Whatever the
   mount passes, no card of the landscape form draws in, the last card keeps its outward bearing, and the pose at
   every t of what WOULD be the gather window is the pose it had before P61 T7c - which is what makes its goldens
   byte-identical to `dddccb2`. */
test("the full frame keeps the reference: no gather, the last card recedes, the throw leaves the rail", () => {
  const n = 6, ats = [3, 5, 7, 9, 11, 13];
  const its = ats.map((at, i) => Object.assign({ at }, verdictGeometry(i, W, H, VERDICT, n)));
  for (let i = 0; i < n; i++) {
    assert.deepEqual([its[i].gx, its[i].gy, its[i].last], [0, 0, false], `card ${i} carries a gather on the full frame`);
    const raw = verdictGeometry(i, W, H);                       // the caller that knows one card: no `n` at all
    assert.deepEqual([its[i].bx, its[i].by], [raw.bx, raw.by], `card ${i}'s bearing moved with the wall's count`);
  }
  // the pose across the window the short would gather in is FLAT against the same pose with no wall count at all
  const solo = ats.map((at, i) => Object.assign({ at }, verdictGeometry(i, W, H)));
  for (let k = 0; k <= 27; k++) {
    const t = 20 - 0.9 + k / 30;
    for (let i = 0; i < n; i++) {
      const a = verdictPose(its[i], i, t, verdictNextAt(its, i, 20), 20);
      const b = verdictPose(solo[i], i, t, verdictNextAt(solo, i, 20), 20);
      assert.deepEqual([a.tx, a.ty, a.scale], [b.tx, b.ty, b.scale], `card ${i} moved at t ${t.toFixed(3)}`);
    }
  }
  // the throw's origin is the RAIL (no rest pose): its first burst frame is the tilt and no offset
  const b0 = verdictBurst(its[0], 0, 20, 20);
  assert.deepEqual([b0.tx, b0.ty, b0.scale, b0.rot], [0, 0, 1, its[0].tilt]);
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
  /* P61 T7d: the full frame's burst string is the INLINE code's, unrounded - the gathering form's rounded one is
     pinned by the 9:16 goldens. The two spellings are why byte identity needed more than the dials (E99 s61). */
  const b = verdictBurst(its[1], 1, 10.2, 10);
  assert.equal(its[1].card.style.transform,
    `translate(${b.tx}px, ${b.ty}px) translateZ(${b.tz}px) rotate(${b.rot}deg) scale(${b.scale})`);
  assert.match(its[1].card.style.transform, /^translate\([-\d.e]+px, [-\d.e]+px\) translateZ\([\d.e-]+px\) rotate\([-\d.e]+deg\) scale\([\d.e-]+\)$/);
  assert.equal(removed, 0);
  assert.equal(paintVerdict(st, 10 + 1.41, { enter: 2 }), false);
  assert.equal(paintVerdict(st, 1.4, { enter: 2 }), false);
  assert.equal(removed, 2);
});
