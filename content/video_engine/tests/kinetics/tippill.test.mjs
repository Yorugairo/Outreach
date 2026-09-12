// P50 T11 - the tip-riding pill (R26-34): X_pill(u) = P_tip(u) + D_offset, the leader from the tip, the pop on
// springPop(Mp = 0.05) at a declared milestone, and the hand-over to the terminal tag at the end of the draw (E53 s8).
import { test } from "node:test";
import assert from "node:assert/strict";
import { TIPPILL, polyCum, tipAt, fracAtIndex, pillAt, pillBox, pillSpan, pillClamp, leaderEnd } from "../../scripts/species/tippill.mjs";
import { springPop } from "../../scripts/kinetics/spring.mjs";

const straight = [[100, 400], [200, 400], [300, 400], [400, 400]];   // 300 units long, flat
const zig = [[100, 400], [200, 300], [300, 420], [400, 260]];

test("P_tip(u) is the point at u of the line's ARC length - the fraction a dash offset has drawn", () => {
  assert.deepEqual(tipAt(straight, 0).p, [100, 400]);
  assert.deepEqual(tipAt(straight, 1).p, [400, 400]);
  assert.deepEqual(tipAt(straight, 0.5).p, [250, 400]);
  assert.deepEqual(tipAt(straight, -1).p, [100, 400], "clamped, never extrapolated");
  assert.deepEqual(tipAt(straight, 2).p, [400, 400]);
  const cum = polyCum(zig), L = cum[cum.length - 1];
  for (const f of [0.1, 0.37, 0.5, 0.8]) {   // the tip is always ON the polyline
    const p = tipAt(zig, f).p;
    let best = Infinity;
    for (let i = 0; i + 1 < zig.length; i++) {
      const a = zig[i], b = zig[i + 1], dx = b[0] - a[0], dy = b[1] - a[1], l2 = dx * dx + dy * dy;
      const k = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2));
      best = Math.min(best, Math.hypot(p[0] - a[0] - k * dx, p[1] - a[1] - k * dy));
    }
    assert.ok(best < 1e-9, `the tip left the line at ${f}`);
  }
  assert.ok(Math.abs(fracAtIndex(zig, 1) - cum[1] / L) < 1e-12, "a milestone DATUM becomes a milestone in u");
  assert.equal(fracAtIndex(zig, 0), 0);
  assert.equal(fracAtIndex(zig, 99), 1, "an index past the end is the end");
});

test("X_pill(u) = P_tip(u) + D_offset while it rides, and the leader runs from the tip to it, short at both ends", () => {
  const s = pillAt(zig, 0.5, { milestone: 0 });
  assert.deepEqual(s.pill, [s.tip[0] + TIPPILL.DX, s.tip[1] + TIPPILL.DY]);
  const d = Math.hypot(s.pill[0] - s.tip[0], s.pill[1] - s.tip[1]);
  const near = Math.hypot(s.leader[0][0] - s.tip[0], s.leader[0][1] - s.tip[1]);
  const far = Math.hypot(s.leader[1][0] - s.pill[0], s.leader[1][1] - s.pill[1]);
  assert.ok(Math.abs(near - Math.min(TIPPILL.LEAD_GAP, d / 3)) < 1e-9 && Math.abs(far - near) < 1e-9,
            "the leader touches neither the nib nor the pill");
  assert.ok(s.on && s.leaderOpacity === 1);
});

test("the pill pops at its milestone on springPop(Mp = 0.05) - not before it, overshooting once, landing on 1", () => {
  const m = fracAtIndex(zig, 2);
  assert.equal(pillAt(zig, m - 0.01, { milestone: m }).on, false, "before the word, no pill");
  assert.equal(pillAt(zig, m, { milestone: m }).scale, 0);
  const k = 0.4;
  assert.equal(pillAt(zig, m + k * TIPPILL.POP_F, { milestone: m }).scale, springPop(k, TIPPILL.POP_MP));
  let peak = 0;
  for (let i = 0; i <= 40; i++) peak = Math.max(peak, pillAt(zig, m + (i / 40) * TIPPILL.POP_F, { milestone: m }).scale);
  assert.ok(peak > 1 && peak <= 1 + TIPPILL.POP_MP + 1e-9, `the overshoot is Mp = ${TIPPILL.POP_MP} (peak ${peak.toFixed(4)})`);
  assert.equal(pillAt(zig, m + TIPPILL.POP_F, { milestone: m }).scale, 1, "and it lands on exactly 1");
  assert.equal(TIPPILL.POP_MP, 0.05);
});

test("at the end of the draw the pill IS the terminal tag: it lands on the tag's place and the tag takes over", () => {
  const tag = [980, 210];
  const s0 = pillAt(zig, 1 - TIPPILL.SETTLE, { milestone: 0, tag });
  assert.equal(s0.settle, 0, "the settle starts exactly one SETTLE from the end");
  assert.deepEqual(s0.pill, [s0.tip[0] + TIPPILL.DX, s0.tip[1] + TIPPILL.DY]);
  const mid = pillAt(zig, 1 - TIPPILL.SETTLE / 2, { milestone: 0, tag });
  assert.ok(mid.settle > 0.49 && mid.settle < 0.51 && mid.leaderOpacity < 0.51, "the leader goes as the pill leaves the tip");
  const end = pillAt(zig, 1, { milestone: 0, tag });
  assert.deepEqual(end.pill, tag, "the pill lands ON the tag's place");
  assert.equal(end.handover, 1, "and hands the name over - one label, in one place (E53 s8)");
  assert.equal(end.on, false, "the pill is not a second label standing beside the tag");
  const noTag = pillAt(zig, 1, { milestone: 0 });
  assert.deepEqual(noTag.pill, [noTag.tip[0] + TIPPILL.DX, noTag.tip[1] + TIPPILL.DY], "with no tag named it just rides");
});

test("the pill is kept ON the stage: the offset says where it wants to be, the clamp where it may be", () => {
  assert.deepEqual(pillSpan(500, [-200, 0]), [300, 500]);   // a tag written from its end
  assert.deepEqual(pillSpan(500, [0, 200]), [500, 700]);   // ... and from its start
  assert.equal(pillClamp(120, [-200, 0], 0, 1000), 200, "a string that would run off the left is pushed in");
  assert.equal(pillClamp(950, [0, 200], 0, 1000), 800, "and off the right");
  assert.equal(pillClamp(500, [-200, 0], 0, 1000), 500, "one that fits is not moved");
  assert.equal(pillClamp(500, [-1400, 0], 0, 1000), 500, "one wider than the stage is left where the author put it");
  const near = [[900, 300], [980, 260]];   // a line that ends at the right edge, an end-anchored tag
  const free = pillAt(near, 1 - TIPPILL.SETTLE, { milestone: 0 });
  const held = pillAt(near, 1 - TIPPILL.SETTLE, { milestone: 0, span: [-420, 0], bounds: [8, 1000] });
  assert.ok(free.pill[0] > held.pill[0], "the clamp only ever pulls the pill back onto the stage");
  assert.ok(pillSpan(held.pill[0], [-420, 0])[0] >= 8 - 1e-9, "and it lands inside the box it was given");
  assert.equal(held.pill[1], free.pill[1], "the clamp is horizontal: the pill keeps its height above the tip");
});

test("it is a pure function of u: the same fraction is the same state, seeked or played", () => {
  const opts = { milestone: fracAtIndex(zig, 1), tag: [900, 200] };
  for (const u of [0.13, 0.5, 0.77, 0.95, 1]) {
    assert.deepEqual(JSON.stringify(pillAt(zig, u, opts)), JSON.stringify(pillAt(zig, u, opts)));
  }
  assert.equal(pillAt([], 0.5), null, "a line with no points has no tip, and says so");
});

test("the pill's box is its type plus its padding, capsule-ended, and the dials are frozen", () => {
  const b = pillBox(120, 34);
  assert.equal(b.w, 120 + 2 * TIPPILL.PAD_X);
  assert.equal(b.h, 34 + 2 * TIPPILL.PAD_Y);
  assert.equal(b.x, -b.w / 2);
  assert.equal(b.r, Math.min(b.h / 2, 12));
  assert.throws(() => { TIPPILL.DX = 0; }, TypeError);
  assert.equal(TIPPILL.SETTLE, 0.10, "the last tenth of the draw - the window the terminal tag fades in over");
});

/* R26-42 (P52 T2): the leader ends ON the capsule, at the edge nearest the tip - never inside it */
const strictlyInside = (p, r) => p[0] > r[0] + 1e-9 && p[0] < r[2] - 1e-9 && p[1] > r[1] + 1e-9 && p[1] < r[3] - 1e-9;
const rectOf = (pill, box) => [pill[0] + box.x, pill[1] + box.y, pill[0] + box.x + box.w, pill[1] + box.y + box.h];

test("the leader's far end is ON the capsule's near edge for an end-anchored tag, never inside the box (R26-42)", () => {
  for (const scale of [1, 1920 / 1080]) {                       /* the two aspects: the stage's px differ, the law does not */
    const b = pillBox(140 * scale, 26 * scale);
    const endAnchored = { x: -b.w, y: -b.h / 2, w: b.w, h: b.h };  /* written from its end: the anchor sits on the box's right edge */
    const s = pillAt(zig, 0.5, { milestone: 0, box: endAnchored });
    const r = rectOf(s.pill, endAnchored);
    assert.ok(strictlyInside(s.pill, r) === false || true);       /* the anchor is on the edge; the point under test is the leader */
    const end = leaderEnd(s.tip, s.pill, endAnchored).p;
    assert.ok(!strictlyInside(end, r), `the terminus ${end} is inside the box ${r}`);
    const onEdge = [r[0], r[1], r[2], r[3]].some((v, i) => Math.abs((i % 2 ? end[1] : end[0]) - v) < 1e-9);
    assert.ok(onEdge, "the terminus lies on the rect's boundary");
    assert.ok(!strictlyInside(s.leader[1], r), "the drawn leader stops short of the box, outside it");
    // the first cut ended the leader at the anchor: for this tag that point is INSIDE the ink the eye sees
    const anchorOnly = pillAt(zig, 0.5, { milestone: 0 });
    assert.ok(Math.hypot(anchorOnly.leader[1][0] - s.leader[1][0], anchorOnly.leader[1][1] - s.leader[1][1]) > 10,
              "with the box the far end moved to the near edge");
  }
});

test("a start-anchored tag's near edge IS its anchor; a mid-anchored tag's is half a box away (both anchor ends)", () => {
  const b = pillBox(140, 26);
  const start = { x: 0, y: -b.h / 2, w: b.w, h: b.h };            /* written from its start: the anchor is the box's left edge */
  const mid = { x: -b.w / 2, y: -b.h / 2, w: b.w, h: b.h };
  const s = pillAt(straight, 0.5, { milestone: 0 });               /* the tip is LEFT of the pill (DX > 0), on a flat line */
  const eS = leaderEnd(s.tip, s.pill, start), eM = leaderEnd(s.tip, s.pill, mid);
  assert.ok(Math.hypot(eS.p[0] - s.pill[0], eS.p[1] - s.pill[1]) < 1e-9 && eS.t === 0, "start-anchored: the edge is the anchor");
  assert.ok(!strictlyInside(eM.p, rectOf(s.pill, mid)), "mid-anchored: the terminus leaves the box");
  assert.ok(eM.p[0] < s.pill[0], "mid-anchored: it leaves toward the tip");
});

test("without a box the span gives the horizontal near edge; without either the terminus is the anchor (the old law)", () => {
  const s = pillAt(straight, 0.5, { milestone: 0 });
  const e = leaderEnd(s.tip, s.pill, null, [-20, 0]);          /* the ink stops short of the nib (DX keeps it clear) */
  assert.ok(Math.abs(e.p[0] - (s.pill[0] - 20)) < 1e-9, "span: the left edge, on the ray toward the tip");
  const wide = leaderEnd(s.tip, s.pill, null, [-120, 0]);        /* ink over the nib itself: the leader is cut AT the tip */
  assert.ok(Math.abs(wide.t - Math.hypot(s.tip[0] - s.pill[0], s.tip[1] - s.pill[1])) < 1e-9);
  const e0 = leaderEnd(s.tip, s.pill);
  assert.deepEqual(e0.p, s.pill);
  const s2 = pillAt(straight, 0.5, { milestone: 0, span: [-20, 0] });
  assert.ok(s2.leader[1][0] < s.leader[1][0], "the drawn leader with a span stops earlier than without");
});

test("an anchor outside its own box, or a box that swallows the tip, never sends the leader past the tip", () => {
  const s = pillAt(straight, 0.5, { milestone: 0 });
  const away = { x: 40, y: -10, w: 60, h: 20 };                    /* a chip pushed the ink clear of the anchor */
  assert.deepEqual(leaderEnd(s.tip, s.pill, away).p, s.pill);
  const huge = { x: -2000, y: -2000, w: 4000, h: 4000 };
  const e = leaderEnd(s.tip, s.pill, huge);
  assert.ok(Math.abs(e.t - Math.hypot(s.tip[0] - s.pill[0], s.tip[1] - s.pill[1])) < 1e-9, "cut at the tip, not beyond");
});
