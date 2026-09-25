// P47 T5 - the idle (ruling E49: "nothing ever goes truly still"). Every kind is a pure function of t, sized by its dial,
// above rest for a breath, bounded for a drift, asymmetric for a figure - and `none` is the identity to the string.
import { test } from "node:test";
import assert from "node:assert/strict";
import { IDLE, IDLE_KINDS, idleClock, breath, drift, pulse, figureBreath, figurePhases, sway, idleXf, idleCss } from "../../scripts/kinetics/idle.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the kinds are the E49 names (live restored by R26-93) and the dials carry the starting references", () => {
  assert.deepEqual([...IDLE_KINDS], ["none", "breath", "drift", "pulse", "figure", "live"]);
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

test("R26-93: live is exactly breath + drift, so a chart at the page centre moves (dx/dy and scale both change)", () => {
  assert.ok(IDLE_KINDS.includes("live"));
  let moved = false, scaled = false;
  for (let i = 0; i <= 60; i++) {   /* t in [0, 2] s at 30 fps */
    const t = i / 30, l = idleXf("live", t), b = idleXf("breath", t), d = idleXf("drift", t);
    if (l.dx !== 0 || l.dy !== 0) moved = true;
    if (l.scale !== 1) scaled = true;
    assert.equal(l.scale, b.scale, `t=${t}: scale is the breath's`);
    assert.equal(l.dx, d.dx, `t=${t}: dx is the drift's`);
    assert.equal(l.dy, d.dy, `t=${t}: dy is the drift's`);
    assert.equal(l.lum, 1);
  }
  assert.ok(moved, "live translates: the pixel at the page centre is never still");
  assert.ok(scaled, "live breathes");
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

/* ---------------------------------------------------------------------------------------------------------------
   P70 T13 - THE DRIFT-HOLD (HyperFrames drift-hold): a held card turns under a degree, breathes and carries one light
   sweep, each ONE whole cycle across its held span, the seam exact; the dials are the reference's own. */
import * as IDLEMOD from "../../scripts/kinetics/idle.mjs";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const HERE = fileURLToPath(new URL(".", import.meta.url));
const REF = readFileSync(HERE + "../../hyperframes/compositions/components/drift-hold.html", "utf8");
const SRC = readFileSync(HERE + "../../scripts/kinetics/idle.mjs", "utf8");
const H = () => IDLEMOD.IDLE_HOLD;
const poseAt = (t, span, grade) => IDLEMOD.idleXf(grade ? "hold:" + grade : "hold", t, 0.37, { HOLD_SPAN: span });
const sgnChanges = (xs) => { let n = 0; for (let i = 1; i < xs.length; i++) if (Math.sign(xs[i]) !== Math.sign(xs[i - 1]) && xs[i] !== 0) n++; return n; };

test("T13: hold is a named CARD kind that turns and breathes (today an unknown kind is stillness)", () => {
  assert.deepEqual([...IDLEMOD.IDLE_CARD_KINDS], ["hold", "hold:whisper", "hold:standard"], "E49: every idle is a NAMED kind");
  assert.ok(!IDLE_KINDS.includes("hold"), "a card's kind, never a plate's, a page's or a species'");
  assert.ok(H(), "IDLE_HOLD, the drift-hold's dials");
  const x = poseAt(0.5, [0, 4]);   /* an eighth of the cycle: every channel off its rest */
  assert.ok(x.rot !== undefined && x.scale !== 1, "a hold turns and breathes - never the identity an unknown kind gets");
});

test("T13: the dials are drift-hold.html's own amplitudes and phases, and every dial line carries a DERIVED tag", () => {
  const m = /whisper:\s*\{\s*rotation:\s*([\d.]+),\s*scale:\s*([\d.]+),\s*sweep:\s*([\d.]+),\s*light:\s*([\d.]+)\s*\},\s*standard:\s*\{\s*rotation:\s*([\d.]+),\s*scale:\s*([\d.]+),\s*sweep:\s*([\d.]+),\s*light:\s*([\d.]+)\s*\}/.exec(REF);
  assert.ok(m, "the reference's amplitudes table is where the test reads it");
  const ref = { whisper: m.slice(1, 5).map(Number), standard: m.slice(5, 9).map(Number) };
  const cardCqw = +/\.dh-card\s*\{[^}]*?width:\s*([\d.]+)cqw/.exec(REF)[1];
  assert.equal(cardCqw, 68);
  for (const g of IDLEMOD.IDLE_HOLD_GRADES) {
    const A = H()[g], [rot, scale, sweep, light] = ref[g];
    assert.equal(A.ROT_DEG, rot, g + " rotation");
    assert.equal(A.SCALE, scale, g + " scale");
    assert.ok(near(A.SWEEP * cardCqw, sweep, 1e-12), g + " sweep, in the reference's cqw");
    assert.equal(A.LIGHT, light, g + " light");
  }
  assert.ok(near(H().BAND_W * cardCqw, +/\.dh-sweep\s*\{[^}]*?width:\s*([\d.]+)cqw/.exec(REF)[1], 1e-12), "the band's width");
  assert.equal(H().BAND_LEFT * 100, +/\.dh-sweep\s*\{[^}]*?left:\s*([\d.]+)%/.exec(REF)[1], "the band's rest");
  assert.equal(H().BAND_TILT_DEG, +/rotation:\s*(\d+),\s*\n\s*opacity/.exec(REF)[1], "the band's lean");
  assert.equal(H().LIGHT_BASE, +/sweepOpacity = ([\d.]+) \+/.exec(REF)[1], "the light's base");
  assert.equal(H().FREE_S, +/data-duration="([\d.]+)"/.exec(REF)[1], "the reference's mounted duration");
  for (const [k, re] of [["PH_ROT", /rotation = Math\.sin\(phase \+ Math\.PI \/ (\d+)\)/], ["PH_SCALE", /scale = 1 \+ Math\.sin\(phase \+ Math\.PI \/ (\d+)\)/],
                         ["PH_LIGHT", /sweepOpacity = [\d.]+ \+ Math\.sin\(phase \+ Math\.PI \/ (\d+)\)/]])
    assert.ok(near(H()[k], Math.PI / +re.exec(REF)[1]), k);
  assert.ok(near(H().PH_SWEEP, -Math.PI / +/sweepX = Math\.sin\(phase - Math\.PI \/ (\d+)\)/.exec(REF)[1]), "PH_SWEEP");
  /* every numeric line of the IDLE_HOLD block names where its number came from */
  const block = SRC.slice(SRC.indexOf("export const IDLE_HOLD = "), SRC.indexOf("export const IDLE_HOLD_GRADES"));
  const dialLines = block.split("\n").filter((l) => /^\s+[A-Z_]+:\s*[-\d[(M]/.test(l));
  assert.ok(dialLines.length >= 18, "the dials are all there: " + dialLines.length);
  for (const l of dialLines) assert.match(l, /\[DERIVED: /, "untagged dial: " + l.trim());
});

test("T13: one whole cycle across the held span - the pose at t0 IS the pose at t1, to the bit, at any span", () => {
  for (const span of [[2.0, 2.8], [10.0, 13.7], [100.25, 112.59]]) for (const g of ["whisper", "standard"]) {
    const a = poseAt(span[0], span, g), b = poseAt(span[1], span, g);
    assert.deepEqual(a, b, `${g} ${span}: the seam`);
    assert.deepEqual(poseAt(span[0] - 0.5, span, g), a, "before the span it holds the seam pose");
    assert.deepEqual(poseAt(span[1] + 0.5, span, g), a, "after the span it holds the seam pose (a retract carries it)");
    const rots = [], scales = [], sweeps = [];
    const n = Math.round((span[1] - span[0]) * 30);   /* 30 fps */
    for (let i = 0; i <= n; i++) { const x = poseAt(span[0] + (span[1] - span[0]) * i / n, span, g); rots.push(x.rot); scales.push(x.scale - 1); sweeps.push(x.sweep); }
    assert.equal(sgnChanges(rots), 2, `${g} ${span}: the turn is ONE sine cycle (two zero crossings), not a loop`);
    assert.equal(sgnChanges(scales), 2, `${g} ${span}: the breath is ONE cycle`);
    assert.equal(sgnChanges(sweeps), 2, `${g} ${span}: the sweep crosses and returns ONCE`);
  }
});

test("T13: it turns UNDER a degree and stays restrained; whisper is under standard on every channel", () => {
  for (const g of ["whisper", "standard"]) {
    let rmax = 0, smax = 0, lmin = 1, lmax = 0;
    for (let i = 0; i <= 4000; i++) { const x = poseAt(i / 1000, [0, 4], g); rmax = Math.max(rmax, Math.abs(x.rot)); smax = Math.max(smax, Math.abs(x.scale - 1)); lmin = Math.min(lmin, x.light); lmax = Math.max(lmax, x.light); }
    assert.ok(rmax < 1 && near(rmax, H()[g].ROT_DEG, 1e-4), `${g}: |rot| ${rmax} < 1 deg`);
    assert.ok(near(smax, H()[g].SCALE, 1e-6), `${g}: the breath's reach`);
    assert.ok(lmin > 0 && near(lmax, H().LIGHT_BASE + H()[g].LIGHT, 1e-4), `${g}: the light never goes negative`);
  }
  for (const k of ["ROT_DEG", "SCALE", "SWEEP", "LIGHT"]) assert.ok(H().whisper[k] < H().standard[k], k);
  assert.equal(IDLEMOD.holdGradeOf("hold"), "standard", "an unqualified hold is standard (the compiler resolves the grade by payload)");
  assert.equal(IDLEMOD.holdGradeOf("hold:whisper"), "whisper");
  assert.equal(IDLEMOD.holdGradeOf("hold:loud"), null);
  assert.equal(IDLEMOD.holdGradeOf("breath"), null);
});

test("T13: idleCss writes the turn for a hold; every older kind writes exactly the string it always wrote", () => {
  const old = (x) => (x.scale === 1 && x.dx === 0 && x.dy === 0) ? "" : " translate(" + x.dx.toFixed(2) + "px," + x.dy.toFixed(2) + "px) scale(" + x.scale.toFixed(4) + ")";
  for (const k of ["none", "breath", "drift", "pulse", "figure", "live"]) for (let i = 0; i < 200; i++) {
    const x = idleXf(k, i * 0.137, 0.29);
    assert.equal(idleCss(x), old(x), `${k} @ ${i * 0.137}`);
  }
  const h = poseAt(11.0, [10, 16], "standard");
  assert.match(idleCss(h), /^ translate\(0\.00px,0\.00px\) scale\(\d\.\d{4}\) rotate\(-?\d\.\d{3}deg\)$/);
  assert.equal(idleCss(h), idleCss(poseAt(11.0, [10, 16], "standard")), "a seek is the play");
});

test("T13: a span-less hold still lives - it cycles on the reference's own mounted duration", () => {
  const a = IDLEMOD.idleXf("hold", 1.3, 0.2), b = IDLEMOD.idleXf("hold", 1.3 + H().FREE_S, 0.2);
  assert.ok(near(a.rot, b.rot, 1e-9) && near(a.scale, b.scale, 1e-12));
  assert.notEqual(IDLEMOD.idleXf("hold", 1.3, 0.2).rot, IDLEMOD.idleXf("hold", 2.3, 0.2).rot);
});

test("T13 / E28: the light is one soft band across the card, and its peak never takes our text under AAA contrast", () => {
  assert.equal(IDLEMOD.holdLightCss({ sweep: 0, light: 0.1 }, 0, 100), "");
  const css = IDLEMOD.holdLightCss(IDLEMOD.holdPose(1.0, "standard"), 800, 450);
  const stops = [...css.matchAll(/rgba\(242,242,242,([\d.]+)\) (-?[\d.]+)%/g)].map((m) => [+m[1], +m[2]]);
  assert.equal(stops.length, 5, css);
  for (let i = 1; i < 5; i++) assert.ok(stops[i][1] > stops[i - 1][1], "stops ascend");
  assert.equal(stops[0][0], 0); assert.equal(stops[4][0], 0);
  assert.ok(stops[2][0] > stops[1][0] && stops[2][0] <= IDLEMOD.holdPeakAlpha("standard") + 1e-4, "the peak is the centre, and it is bounded");
  /* the band travels: its centre is left of the rest at the seam, right of it at mid-hold */
  const centre = (ph) => +/rgba\(242,242,242,[\d.]+\) (-?[\d.]+)%, rgba\(242,242,242,[\d.]+\) (-?[\d.]+)%, rgba/.exec(IDLEMOD.holdLightCss(IDLEMOD.holdPose(ph, "standard"), 800, 450))[2];
  assert.ok(centre(0) < centre(Math.PI) - 40, "the sweep crosses the card");
  /* E28: WCAG contrast of the text the card carries, with the band's PEAK laid over text and ground alike */
  const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  const lum = (r) => 0.2126 * lin(r[0]) + 0.7152 * lin(r[1]) + 0.0722 * lin(r[2]);
  const over = (c, a) => c.map((v, i) => v * (1 - a) + H().INK[i] * a);
  const cr = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const CHALK = [242, 242, 242], CHAR = [0x25, 0x31, 0x3C], CREAM = [0xF4, 0xE6, 0xC7], DEEP = [0x14, 0x18, 0x1E];
  for (const [what, ink, ground, g] of [["chart card (chalk on the page's charcoal)", CHALK, CHAR, "whisper"],
                                         ["long-form chart card", CHALK, DEEP, "whisper"],
                                         ["evidence card (charcoal on the dock's cream)", CHAR, CREAM, "standard"]]) {
    const a = IDLEMOD.holdPeakAlpha(g), rest = cr(ink, ground), peak = cr(over(ink, a), over(ground, a));
    assert.ok(peak >= 7, `${what}: ${peak.toFixed(2)}:1 at the light's peak (rest ${rest.toFixed(2)}:1) - WCAG AAA 7:1 held`);
  }
});
