// P70 T7 (was P69 T59) - THE BALANCE SCALE, AND THE BALANCE TIPS (the Bravos harvest v2's T27 and A40, CHN 19:10). The
// whole visual state is a pure function of t and the declaration: the beam's angle is a sum of closed-form spring steps
// (a lone load leans it, both loads settle it LEVEL, a tip swings it with ONE visible overshoot), every generated curve
// is a clothoid (doc 42 s42.4), the pans hang plumb, and the base casts T6b's resting hatch when the ctx hands the
// painter `propHatchLines` (E99 s128: an object in the world). These tests pin all of it, and that nothing is remembered.
import { test } from "node:test";
import assert from "node:assert/strict";
import { springParams, springEval } from "../../scripts/kinetics/spring.mjs";
import { curvatureOf } from "../../scripts/kinetics/clothoid.mjs";
import { STOP } from "../../scripts/kinetics/stopaction.mjs";
import { BALANCE, BALANCE_SIDES, balanceContactS, balanceSteps, balanceAngle, balanceGeom, balanceArm, balanceEnd,
         balanceHanger, balanceBowl, balanceDome, balanceLoadPose, balanceDraw, balanceLeave, balanceNameFit,
         balanceNameRow, paintBalance } from "../../scripts/species/balance.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const ROOM = { x: 1411, y: 238, w: 480, h: 670 };
const bal = (o = {}) => Object.assign({ kind: "balance", at: 11.43, dur: 12.52, target: { kind: "region" },
  left: { label: "MOAT", at: 12.76 }, right: { label: "PAPER", at: 16.65 } }, o);
const C = balanceContactS();

// ---------------------------------------------------------------- the dials
test("the tip's dials give ONE visible overshoot and a swing back under a degree", () => {
  assert.ok(BALANCE.TIP_MP * BALANCE.TIP_DEG >= 1.5, "the first swing past the rest must be SEEN");
  assert.ok(BALANCE.TIP_MP ** 2 * BALANCE.TIP_DEG < 1, "the second is under a degree");
  assert.ok(BALANCE.TIP_DEG >= 10 && BALANCE.TIP_DEG <= 15, "Bravos rests at ~13 deg (CHN shot 114)");
  assert.equal(C, STOP.ANTIC_S + STOP.DROP_S, "the beam answers a load at landXf's CONTACT");
  assert.ok(BALANCE.LABEL_PX >= 59.08, "every name at the s90 phone floor");
  assert.ok(BALANCE.LAND_SEEN_S >= C, "the compiler's landing window covers the contact");
});

// ---------------------------------------------------------------- the weighing
test("unloaded the beam is level; one load leans it toward that side; both settle it LEVEL", () => {
  const sp = bal();
  assert.equal(balanceAngle(sp, sp.at + 0.5), 0);
  assert.equal(balanceAngle(sp, sp.left.at + C), 0, "nothing moves before the contact");
  const leaned = balanceAngle(sp, sp.left.at + C + 3);
  assert.ok(near(leaned, -BALANCE.LEAN_DEG, 1e-3), `the LEFT end goes down (theta < 0): ${leaned}`);
  assert.ok(near(balanceAngle(sp, sp.right.at + C + 3), 0, 1e-3), "both weighed: level");
  const onlyRight = bal({ left: { label: "MOAT", at: 30 } });
  assert.ok(near(balanceAngle(onlyRight, onlyRight.right.at + C + 3), BALANCE.LEAN_DEG, 1e-3), "the right end goes down (theta > 0)");
});

test("the level settle does not care which side came first, or whether both came on one word", () => {
  const a = bal(), b = bal({ left: { label: "MOAT", at: 16.65 }, right: { label: "PAPER", at: 12.76 } });
  const same = bal({ right: { label: "PAPER", at: 12.76 } });
  for (const t of [13.5, 15, 17.2, 20]) {
    assert.ok(near(balanceAngle(a, t), -balanceAngle(b, t), 1e-12), `mirror at ${t}`);
    assert.equal(balanceAngle(same, t), 0, "two loads on one word: one weighing, no lean at all");
  }
});

test("the lean is the lean spring's step response, exactly", () => {
  const sp = bal(), p = springParams(BALANCE.LEAN_MP);
  for (const dt of [0.05, 0.2, 0.4, 0.8]) {
    const want = -BALANCE.LEAN_DEG * springEval(dt / BALANCE.LEAN_S, p).x;
    assert.ok(near(balanceAngle(sp, sp.left.at + C + dt), want, 1e-12), `${dt}`);
  }
});

// ---------------------------------------------------------------- the tip (A40)
test("THE TIP: one visible overshoot past TIP_DEG, the swing back under a degree, then rest - toward the named side", () => {
  const sp = bal({ tip: { at: 20, to: "right" } });
  const p = springParams(BALANCE.TIP_MP), tp = Math.PI / p.wd * BALANCE.TIP_S;   // the peaks of the step, in seconds
  const peak = balanceAngle(sp, sp.tip.at + tp), back = balanceAngle(sp, sp.tip.at + 2 * tp);
  assert.ok(near(peak, BALANCE.TIP_DEG * (1 + BALANCE.TIP_MP), 1e-6), `the first peak is exactly 1 + Mp: ${peak}`);
  assert.ok(peak - BALANCE.TIP_DEG >= 1.5, "... and it is visible");
  assert.ok(BALANCE.TIP_DEG - back < 1 && BALANCE.TIP_DEG - back > 0, `the swing back is under a degree: ${back}`);
  assert.ok(Math.abs(balanceAngle(sp, sp.tip.at + 3 * tp) - BALANCE.TIP_DEG) < 0.12, "the third excursion is gone to the eye");
  assert.ok(near(balanceAngle(sp, sp.tip.at + 2.5), BALANCE.TIP_DEG, 1e-3), "at rest, tipped");
  assert.ok(Math.abs(balanceAngle(sp, sp.tip.at)) < 1e-6, "level on the word (the lean springs' tails are 1e-9), then it goes: a mass, never a jump");
  // it is continuous across the word (no pop) and toward the LEFT it is the mirror
  assert.ok(Math.abs(balanceAngle(sp, sp.tip.at + 1 / 96)) < 0.2, "the first frame after the word barely moves");
  const left = bal({ tip: { at: 20, to: "left" } });
  assert.ok(near(balanceAngle(left, 20 + tp), -peak, 1e-9));
});

test("the steps are the declaration's: a tip with no side, or no word, adds nothing", () => {
  assert.equal(balanceSteps(bal({ tip: { at: 20, to: "up" } })).length, 2);
  assert.equal(balanceSteps(bal({ tip: { to: "left" } })).length, 2);
  assert.deepEqual(balanceSteps(bal({ tip: { at: 20, to: "left" } })).map((s) => s.why), ["left", "right", "tip"]);
});

// ---------------------------------------------------------------- the geometry: clothoids, plumb pans
test("the arms are clothoids: each is the symmetric fit (the circular arc) from the pivot to its end", () => {
  const g = balanceGeom(ROOM);
  for (const side of BALANCE_SIDES) {
    const pts = balanceArm(g.A, side), s = side === "left" ? -1 : 1;
    assert.ok(near(pts[0].x, 0, 1e-9) && near(pts[0].y, 0, 1e-9), "it leaves the pivot");
    assert.ok(near(pts.at(-1).x, s * g.A, 1e-6) && near(pts.at(-1).y, 0, 1e-6), "it lands on its end");
    assert.ok(pts.slice(1, -1).every((p) => p.y < 0), "it arches UP off the chord (y down)");
    const k = curvatureOf(pts).slice(2, -2), mean = k.reduce((a, v) => a + v, 0) / k.length;
    assert.ok(k.every((v) => Math.abs(v - mean) < Math.abs(mean) * 0.02), "one curvature along it: dk/ds = 0, the arc");
  }
});

test("a hanger is the clothoid with both tangents on its chord - straight - and the bowl and the dome are arcs", () => {
  const h = balanceHanger(-60, 220, 8), k = curvatureOf(h);
  assert.ok(k.every((v) => Math.abs(v) < 1e-9), "a string under load is straight");
  const bowl = balanceBowl(140, 28, 220), dome = balanceDome(1650, 900, 120, 26);
  assert.ok(near(Math.max(...bowl.map((p) => p.y)) - 220, 28, 0.2), "the bowl's depth is its dial");
  assert.ok(near(900 - Math.min(...dome.map((p) => p.y)), 26, 0.2), "the dome's rise is its dial");
});

test("a pan hangs from its arm's end, which turns with the beam about the pivot", () => {
  const g = balanceGeom(ROOM);
  const e0 = balanceEnd(g, "right", 0), e = balanceEnd(g, "right", 12);
  assert.ok(near(e0.x, g.cx + g.A) && near(e0.y, g.py));
  assert.ok(near(e.y - g.py, g.A * Math.sin(12 * Math.PI / 180), 1e-9), "the right end goes DOWN for theta > 0");
  assert.ok(near(Math.hypot(e.x - g.cx, e.y - g.py), g.A, 1e-9), "on the arm's circle");
});

// ---------------------------------------------------------------- the loads, the draw, the leave
test("a load lands on its word by landXf, fading in on the chip's clock", () => {
  const L = { label: "MOAT", at: 12.76 };
  assert.equal(balanceLoadPose(L, 12.7), null);
  const a = balanceLoadPose(L, 12.76);
  assert.equal(a.fade, 0);
  assert.ok(a.y <= -BALANCE.LOAD_DROP_PX, "it starts above its pan");
  assert.equal(balanceLoadPose(L, 12.76 + C + 2).phase, "settled");
  assert.ok(Math.abs(balanceLoadPose(L, 12.76 + C + 2).y) < 0.5, "... and rests in it");
});

test("the draw runs base -> beam -> pans on `at`, and the object leaves in its window's last EXIT_S", () => {
  const sp = bal();
  const d0 = balanceDraw(sp, sp.at), d1 = balanceDraw(sp, sp.at + BALANCE.DRAW_S);
  assert.deepEqual([d0.base, d0.beam, d0.pan], [0, 0, 0]);
  assert.deepEqual([d1.base, d1.beam, d1.pan], [1, 1, 1]);
  const mid = balanceDraw(sp, sp.at + BALANCE.DRAW_S * 0.3);
  assert.ok(mid.base > mid.beam && mid.beam > 0 && mid.pan === 0, "one after the other");
  assert.equal(balanceLeave(sp, sp.at + sp.dur - BALANCE.EXIT_S), 1);
  assert.equal(balanceLeave(sp, sp.at + sp.dur), 0);
});

test("THE NAME FIT, round 3's order: fit its half; shrink to the floor; overhang outward under its pan; pin at the margin", () => {
  const cx = ROOM.x + ROOM.w / 2, P = BALANCE.POST_CLEAR, M = BALANCE.STAGE_MARGIN, half = ROOM.w / 2 - P;   // 218 px
  const pl = cx - BALANCE.ARM_K * ROOM.w, pr = cx + BALANCE.ARM_K * ROOM.w;
  const fit = balanceNameFit("left", pl, 150, ROOM, cx, 1920);
  assert.equal(fit.step, "fit"); assert.equal(fit.size, BALANCE.LABEL_PX); assert.equal(fit.x, pl, "under its pan");
  const shr = balanceNameFit("left", pl, half + 2, ROOM, cx, 1920);
  assert.equal(shr.step, "shrunk"); assert.ok(shr.size < BALANCE.LABEL_PX && shr.size >= BALANCE.LABEL_FLOOR);
  assert.ok(Math.abs(shr.w - half) < 1e-9, "its size fitted to the half exactly");
  const ov = balanceNameFit("left", pl, 363, ROOM, cx, 1920);
  assert.equal(ov.step, "overhang"); assert.equal(ov.size, BALANCE.LABEL_FLOOR);
  assert.ok(ov.x + ov.w / 2 <= cx - P + 1e-9, "never across the post's guard");
  assert.ok(ov.x - ov.w / 2 < ROOM.x, "... it overhangs OUTWARD, past the room's edge");
  assert.ok(ov.x <= cx && ov.x >= ov.w / 2 + M - 1e-9, "its centre in its pan's half, its box on the stage");
  const pin = balanceNameFit("right", pr, 363, ROOM, cx, 1920);
  assert.equal(pin.step, "pinned"); assert.ok(Math.abs(pin.x + pin.w / 2 - (1920 - M)) < 1e-9, "pinned at the stage margin");
  assert.ok(pin.x >= cx, "its centre still in its pan's half");
});

test("a name's row: a bare name on its rim riding its load, a pictured load's name under the bowl", () => {
  const g = balanceGeom(ROOM);
  assert.equal(balanceNameRow(g, false, -40), g.H - BALANCE.RIM_LIFT - 40);
  assert.equal(balanceNameRow(g, true, -40), g.H + g.pd + BALANCE.LABEL_GAP + 0.8 * BALANCE.LABEL_PX);
});

// ---------------------------------------------------------------- the painter, on a fake DOM
const mkCtx = (sp, t, hatch = true) => {
  const root = { tag: "svg", children: [], attrs: {} };
  const el = (tag, cls, parent, at) => {
    const e = { tag, cls, attrs: Object.assign({}, at || {}), children: [], dataset: {}, textContent: "",
                setAttribute(k, v) { this.attrs[k] = String(v); } };
    if (parent) parent.children.push(e);
    return e;
  };
  const calls = [];
  const ctx = { sp, t, k: 0.5, dur: sp.dur, svg: root, el, A: {}, seed: 7, si: 0, hash: () => 0.5,
                resolveTarget: () => ROOM, drawOn: (p, f) => p.setAttribute("data-f", f.toFixed(4)),
                idle: () => ({ scale: 1, dx: 0, dy: 0 }) };
  if (hatch) ctx.propHatchLines = (c, x0, y0, W, H, deg, pitch, width) => {
    calls.push(deg); c.setTransform(1, 0, 0, 1, -x0, -y0); c.fillRect(-10, 0, 20, width); c.fillRect(-10, pitch, 20, width);
  };
  return { ctx, root, calls };
};
const all = (n, out = []) => { out.push(n); (n.children || []).forEach((c) => all(c, out)); return out; };
const ser = (n) => JSON.stringify(n, (k, v) => (k === "setAttribute" ? undefined : v));

test("THE PAINTER: the beam carries its angle, the pans are only ever TRANSLATED, the names are at the floor", () => {
  const sp = bal({ tip: { at: 20, to: "right" } });
  for (const t of [11.6, 12.5, 13.4, 17, 20.32, 22]) {
    const { ctx, root } = mkCtx(sp, t);
    paintBalance(ctx);
    const nodes = all(root);
    const beam = nodes.find((n) => n.cls === "bal-beam");
    assert.equal(beam.dataset.deg, balanceAngle(sp, t).toFixed(4));
    for (const p of nodes.filter((n) => n.cls === "bal-pan"))
      assert.match(p.attrs.transform, /^translate\([-0-9.]+ [-0-9.]+\)$/, "plumb: a translate, never a turn");
    for (const l of nodes.filter((n) => n.cls === "bal-label"))
      assert.match(l.attrs.style, /font-size:60px/, "the s90 floor");
  }
});

test("the base rests on T6b's hatch, laid by the ctx's propHatchLines (both families); without it, no shadow", () => {
  const sp = bal();
  const withH = mkCtx(sp, 13), without = mkCtx(sp, 13, false);
  paintBalance(withH.ctx); paintBalance(without.ctx);
  const h = all(withH.root).filter((n) => n.cls === "bal-hatch");
  assert.equal(h.length, 1, "one hatch, under the base");
  assert.deepEqual(withH.calls, [-125, -50], "the prop's own light and its crossing family (PROP_SHADOW)");
  const lines = all(h[0]).filter((n) => n.tag === "path");
  assert.equal(lines.length, 2);
  assert.ok(lines.every((n) => /^M/.test(n.attrs.d) && /^matrix\(/.test(n.attrs.transform)));
  assert.equal(all(without.root).filter((n) => n.cls === "bal-hatch").length, 0, "acceptance 4: no ctx key, no hatch");
});

test("a name with no picture IS the load; a named picture's name hangs under its pan", () => {
  const sp = bal({ left: { label: "MOAT", icon: "factory", at: 12.76 } });
  const { ctx, root } = mkCtx(sp, 18);
  ctx.A = { "icon:factory": JSON.stringify({ vb: [0, 0, 24, 24], el: [{ t: "path", a: { d: "M2 20h20" } }] }) };
  paintBalance(ctx);
  const pans = all(root).filter((n) => n.cls === "bal-pan");
  const left = pans.find((p) => p.dataset.side === "left"), right = pans.find((p) => p.dataset.side === "right");
  assert.ok(all(left).some((n) => n.cls === "bal-glyph"), "the sourced glyph lands in the pan");
  assert.ok(left.children.some((n) => n.cls === "bal-label"), "... and its name hangs under the pan");
  const rl = right.children.find((n) => n.cls === "bal-label");
  assert.equal(rl.dataset.row, "bare", "the bare name stands on its rim ...");
  assert.ok(Math.abs(+rl.attrs.y - (balanceGeom(ROOM).H - BALANCE.RIM_LIFT)) < 0.01, "... riding its load, landed");
  assert.equal(left.children.find((n) => n.cls === "bal-label").dataset.row, "pictured");
});


// Review F8: the seek test must be ABLE to fail. The harness paints through ONE shared ctx and ONE layer (the engine's
// own shape: spTop.replaceChildren(), then the painter, every frame) and is proved by breaking it - a painter that keeps
// one number between calls is caught.
const seekHarness = (painter, sp, times, probe) => {
  const { ctx, root } = mkCtx(sp, probe);
  const paint = (t) => { root.children.length = 0; ctx.t = t; painter(ctx); return ser(root); };
  const cold = paint(probe);
  times.forEach(paint);
  return [cold, paint(probe)];
};

test("SEEK-SAFE: through one shared ctx and layer, the frame at t is the same cold and after any other frames", () => {
  const sp = bal({ tip: { at: 20, to: "left" } });
  for (const probe of [11.7, 12.9, 17.0, 20.35, 23.5]) {
    const [cold, after] = seekHarness(paintBalance, sp, [22, 11.5, 14, 20.1, 16.9], probe);
    assert.equal(after, cold, `t = ${probe}`);
  }
});

test("... and the harness catches a painter that remembers anything between frames", () => {
  let n = 0;
  const leaky = (ctx) => { paintBalance(ctx); ctx.svg.children.push({ tag: "g", attrs: { "data-n": String(n++) }, children: [] }); };
  const [cold, after] = seekHarness(leaky, bal(), [14, 18], 16);
  assert.notEqual(after, cold, "a stateful painter must FAIL the seek test");
});
