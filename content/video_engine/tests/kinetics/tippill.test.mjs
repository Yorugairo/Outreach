// P50 T11 - the tip-riding pill (R26-34): X_pill(u) = P_tip(u) + D_offset, the leader from the tip, the pop on
// springPop(Mp = 0.05) at a declared milestone, and the hand-over to the terminal tag at the end of the draw (E53 s8).
import { test } from "node:test";
import assert from "node:assert/strict";
import { TIPPILL, polyCum, tipAt, fracAtIndex, pillAt, pillBox, pillSpan, pillClamp } from "../../scripts/species/tippill.mjs";
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
