// P47 T5 - the idle (ruling E49: "nothing ever goes truly still"). Every kind is a pure function of t, sized by its dial,
// above rest for a breath, bounded for a drift, asymmetric for a figure - and `none` is the identity to the string.
import { test } from "node:test";
import assert from "node:assert/strict";
import { IDLE, IDLE_KINDS, idleClock, breath, drift, pulse, figureBreath, figurePhases, sway, idleXf, idleCss } from "../../scripts/kinetics/idle.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the kinds are the five E49 names and the dials carry the starting references", () => {
  assert.deepEqual([...IDLE_KINDS], ["none", "breath", "drift", "pulse", "figure"]);
  assert.ok(IDLE.BREATH_AMP >= 0.01 && IDLE.BREATH_AMP <= 0.02, "E49: a breathing scale of 1-2 %");
  assert.ok(IDLE.BREATH_HZ >= 0.20 && IDLE.BREATH_HZ <= 0.30, "48 s48.4: 0.20-0.30 Hz");
  assert.ok(IDLE.FIGURE_IE >= 1.5 && IDLE.FIGURE_IE <= 2.0, "48 s48.4: I:E 1:1.5 to 1:2");
  assert.ok(IDLE.FIGURE_PAUSE_S >= 0.5 && IDLE.FIGURE_PAUSE_S <= 1.0, "48 s48.4: the post-expiratory pause");
  assert.deepEqual(IDLE.SWAY_HZ, [0.15, 0.25]);
});

test("breath is exactly 1 at rest, never below 1, never above 1 + AMP, and periodic at 1 / HZ", () => {
  assert.equal(breath(0), 1);
  let max = 0;
  for (let i = 0; i <= 4000; i++) {
    const t = i / 100, s = breath(t);
    assert.ok(s >= 1 - 1e-12 && s <= 1 + IDLE.BREATH_AMP + 1e-12, `t=${t}: ${s}`);
    max = Math.max(max, s);
    assert.ok(near(breath(t + 1 / IDLE.BREATH_HZ), s, 1e-9), "periodic");
  }
  assert.ok(near(max, 1 + IDLE.BREATH_AMP, 1e-6), "the inhale reaches the full amplitude");
  assert.ok(near(breath(1 / IDLE.BREATH_HZ / 2), 1 + IDLE.BREATH_AMP), "the peak is at the half period");
});

test("two phases never breathe in step; the same t and phase always give the same bits (a seek is the play)", () => {
  const a = [], b = [];
  for (let i = 0; i < 100; i++) { a.push(breath(i / 10, 0.13)); b.push(breath(i / 10, 0.61)); }
  assert.notDeepEqual(a, b);
  for (let i = 0; i < 100; i++) assert.equal(breath(i / 10, 0.13), a[i]);
});

test("drift stays inside its box on both axes and starts at the origin", () => {
  assert.deepEqual(drift(0), [0, 0]);
  for (let i = 0; i <= 20000; i++) {
    const [dx, dy] = drift(i / 100, 0.37);
    assert.ok(Math.abs(dx) <= IDLE.DRIFT_PX + 1e-12 && Math.abs(dy) <= IDLE.DRIFT_PX * 0.6 + 1e-12, `t=${i / 100}`);
  }
});

test("pulse is exactly 1 at rest and never dips below 1 - AMP", () => {
  assert.equal(pulse(0), 1);
  for (let i = 0; i <= 2000; i++) { const v = pulse(i / 100); assert.ok(v <= 1 + 1e-12 && v >= 1 - IDLE.PULSE_AMP - 1e-12); }
});

test("the figure's breath is never a sine: a short inhale, a longer exhale, then a real pause at rest", () => {
  const ph = figurePhases();
  assert.ok(near(ph.period, 1 / IDLE.BREATH_HZ));
  assert.ok(near(ph.exhale / ph.inhale, IDLE.FIGURE_IE, 1e-9), "I:E is the dial");
  assert.ok(near(ph.pause, IDLE.FIGURE_PAUSE_S));
  assert.equal(figureBreath(0), 0);
  assert.ok(near(figureBreath(ph.inhale), 1, 1e-9), "full at the end of the inhale");
  assert.ok(near(figureBreath(ph.inhale + ph.exhale), 0, 1e-9), "empty at the end of the exhale");
  for (let i = 0; i <= 50; i++) {   /* the pause: flat at 0, not a sine's slow turn */
    const t = ph.inhale + ph.exhale + (i / 50) * ph.pause * 0.999;
    assert.equal(figureBreath(t), 0, `pause at ${t}`);
  }
  /* monotone up over the inhale, monotone down over the exhale */
  let prev = 0;
  for (let i = 1; i <= 100; i++) { const v = figureBreath(ph.inhale * i / 100); assert.ok(v >= prev - 1e-12); prev = v; }
  for (let i = 1; i <= 100; i++) { const v = figureBreath(ph.inhale + ph.exhale * i / 100); assert.ok(v <= prev + 1e-12); prev = v; }
  assert.ok(near(figureBreath(ph.period + 0.3), figureBreath(0.3)), "periodic");
});

test("sway is bounded and its two rates never close inside a short", () => {
  for (let i = 0; i <= 9000; i++) { const [x, y] = sway(i / 100); assert.ok(Math.abs(x) <= IDLE.SWAY_PX && Math.abs(y) <= IDLE.SWAY_PX + 1e-12); }
  let repeats = 0;
  const s0 = sway(1.0);
  for (let t = 1.05; t < 60; t += 0.05) if (near(sway(t)[0], s0[0], 1e-9) && near(sway(t)[1], s0[1], 1e-9)) repeats++;
  assert.equal(repeats, 0, "no exact return to the t=1 pose inside 60 s");
});

test("idleXf: none is the identity to the string; each kind moves only its own channel", () => {
  const id = idleXf("none", 3.3, 0.5);
  assert.deepEqual(id, { scale: 1, dx: 0, dy: 0, lum: 1 });
  assert.equal(idleCss(id), "");
  const b = idleXf("breath", 1.0, 0.25);
  assert.ok(b.scale > 1 && b.dx === 0 && b.dy === 0 && b.lum === 1);
  const d = idleXf("drift", 1.0, 0.25);
  assert.ok(d.scale === 1 && (d.dx !== 0 || d.dy !== 0) && d.lum === 1);
  const p = idleXf("pulse", 1.0, 0.25);
  assert.ok(p.scale === 1 && p.dx === 0 && p.lum < 1);
  const f = idleXf("figure", 1.0, 0.25);
  assert.ok(f.scale >= 1 && f.lum === 1);
  assert.deepEqual(idleXf("not-a-kind", 1, 0), id, "an unknown kind is stillness, never a throw");
});

test("idleCss writes fixed decimals so two seeks to one t write one string", () => {
  const s1 = idleCss(idleXf("breath", 2.345, 0.1)), s2 = idleCss(idleXf("breath", 2.345, 0.1));
  assert.equal(s1, s2);
  assert.match(s1, /^ translate\(-?\d+\.\d{2}px,-?\d+\.\d{2}px\) scale\(\d\.\d{4}\)$/);
});

test("STEP_FPS quantises the clock to the frame index: constant inside a frame, stepping between frames", () => {
  assert.equal(idleClock(1.234), 1.234, "continuous by default");
  assert.equal(idleClock(1.234, 12), Math.floor(1.234 * 12) / 12);
  const o = { STEP_FPS: 12 };
  const a = idleXf("breath", 1.00, 0, o), b = idleXf("breath", 1.08, 0, o), c = idleXf("breath", 1.09, 0, o);
  assert.equal(a.scale, b.scale, "1.00 and 1.08 sit in one 12 fps frame");
  assert.notEqual(b.scale, c.scale, "1.09 is the next frame");
});
