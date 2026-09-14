// P57 R26-118 / E88 s7 ("a more living ball, that is wriggling to contain itself, and has real, metallic mass and
// density") - THE LIVING DROP. These pin the four claims the header makes: the ring's AREA is pi R^2 at any t (the
// drop is incompressible - it wobbles, it never grows), mode l has exactly l lobes, the impulse's amplitude decays by
// exp(-t / tau) on Lamb's modulus, and the FLOOR (E49) never lets the surface come to rest. Plus the purity every
// scrubbed frame is built on: the same t twice is the same ring, vertex for vertex.
import { test } from "node:test";
import assert from "node:assert/strict";
import { DROP, dropOmega, dropTau, dropAmp, dropModes, dropRadius, dropArea, dropRing, dropSpecular }
  from "../../scripts/kinetics/drop.mjs";

const R = 60;                      // a page ball: 60 px is 7.1 mm at PX_PER_M
const HIT = [{ at: 0, a: DROP.KICK }];
const near = (a, b, tol, what) => assert.ok(Math.abs(a - b) <= tol, `${what}: ${a} vs ${b} (tol ${tol})`);

test("the dials are frozen and the modes are Rayleigh's l = 2, 3, 4", () => {
  assert.equal(Object.isFrozen(DROP), true);
  assert.deepEqual(DROP.MODES, [2, 3, 4]);   // l = 0 is a breath an incompressible drop cannot take, l = 1 a translation
});

test("omega_l follows Rayleigh 1879: omega_3 = sqrt(30/8) omega_2 and omega_4 = 3 omega_2", () => {
  const w2 = dropOmega(2, R, "metal"), w3 = dropOmega(3, R, "metal"), w4 = dropOmega(4, R, "metal");
  near(w3 / w2, Math.sqrt(30 / 8), 1e-12, "mode 3 against mode 2");
  near(w4 / w2, 3, 1e-12, "mode 4 against mode 2");
  // and omega^2 ~ 1 / R^3: a ball twice as big rings 2^1.5 times slower
  near(dropOmega(2, 2 * R, "metal") * Math.pow(2, 1.5), w2, 1e-9, "the R^-3/2 law");
  // the band the CRAFT reads: a wobble is two to three drawings on 2s - a period of 167-250 ms
  const T2 = 2 * Math.PI / w2;
  assert.ok(T2 > 0.167 && T2 < 0.250, `mode 2's period: ${T2}`);
});

test("tau_l follows Lamb 1932: tau_2 / tau_3 = (2*7) / (1*5), and DAMP scales it", () => {
  near(dropTau(2, R, "metal") / dropTau(3, R, "metal"), (2 * 7) / (1 * 5), 1e-12, "the mode ratio");
  near(dropTau(2, R, "metal", { DAMP: 2 * DROP.DAMP }), 2 * dropTau(2, R, "metal"), 1e-9, "DAMP is a scale");
  assert.ok(dropTau(2, R, "metal") > dropTau(2, R, "ink"), "mercury rings longer than ink");
});

test("an impulse decays by exp(-t / tau) - the envelope, read at the peaks", () => {
  const tau = dropTau(2, R, "metal"), w = dropOmega(2, R, "metal"), T = 2 * Math.PI / w;
  for (const n of [1, 2, 3]) {
    const t = n * T;                                  // a whole period: cos = 1, so the value IS the envelope
    near(dropAmp(2, 0.1, t, R, "metal"), 0.1 * Math.exp(-t / tau), 1e-12, `peak ${n}`);
  }
  assert.equal(dropAmp(2, 0.1, -0.01, R, "metal"), 0, "an impulse that has not happened moves nothing");
});

test("mode l alone has exactly l lobes round the ring", () => {
  for (const l of DROP.MODES) {
    const modes = [{ l, a: 0.12, phi: 0.3 }];
    let lobes = 0;
    const n = 720, r = (i) => dropRadius(2 * Math.PI * (((i % n) + n) % n) / n, modes);
    for (let i = 0; i < n; i++) if (r(i) > r(i - 1) && r(i) >= r(i + 1)) lobes++;
    assert.equal(lobes, l, `mode ${l}`);
  }
});

test("the ring's area is pi R^2 at any t - the drop is incompressible", () => {
  const want = Math.PI * R * R;
  for (const t of [0, 0.017, 0.083, 0.25, 0.5, 1.0, 1.6]) {
    for (const mat of ["metal", "ink", "liquid"]) {
      const got = dropArea(dropRing([100, 100], R, t, mat, HIT));
      near(got / want, 1, 1e-6, `${mat} at t=${t}`);
    }
  }
});

test("the ring is NOT the circle (the compile's own excitation is on it) and every point is finite", () => {
  const ring = dropRing([0, 0], R, 0.02, "metal", [{ at: 0, a: DROP.A }]);
  assert.equal(ring.length, DROP.N);
  const rs = ring.map((p) => Math.hypot(p[0], p[1]));
  assert.ok(Math.max(...rs) - Math.min(...rs) > 0.05 * R, "a landed drop is out of round");
  assert.ok(rs.every((v) => Number.isFinite(v) && v > 0));
});

test("the FLOOR never lets it rest: long after every impulse the surface still moves (E49)", () => {
  let worst = 0;
  for (let i = 0; i < 240; i++) {                       // 2 s, 10 s after the hit - every mode's decay is long gone
    const modes = dropModes(10 + i / 120, R, "metal", HIT);
    worst = Math.max(worst, Math.abs(modes[0].a));
  }
  assert.ok(worst > 0.9 * DROP.FLOOR[0], `the floor holds: ${worst} vs ${DROP.FLOOR[0]}`);
  const dead = dropModes(10, R, "metal", HIT, { FLOOR: [0, 0, 0] });
  assert.ok(Math.abs(dead[0].a) < 1e-9, "without the floor it would be dead - which is the point");
});

test("a spin turns the lobes with the surface and the light does not follow", () => {
  const a = dropModes(0.1, R, "metal", HIT), b = dropModes(0.1, R, "metal", HIT, { spin: Math.PI / 6 });
  for (let i = 0; i < a.length; i++) near(b[i].phi - a[i].phi, -a[i].l * Math.PI / 6, 1e-12, `mode ${a[i].l} phase`);   // -l*spin: the pattern turns BY +spin
  // the same theta on the turned surface is the radius the untuned one had one sixth of a turn back
  near(dropRadius(0.7 + Math.PI / 6, b), dropRadius(0.7, a), 1e-12, "the ink turned");
  const hl = dropSpecular([0, 0], R, b);
  near(Math.atan2(hl.y, hl.x), DROP.LIGHT_DEG * Math.PI / 180, 1e-12, "the highlight stays on the light");
  assert.ok(hl.r > 0 && hl.r < R, "the spot is on the ball");
});

test("two calls at one t are identical, vertex for vertex", () => {
  const a = dropRing([12, 34], R, 0.37, "metal", HIT), b = dropRing([12, 34], R, 0.37, "metal", HIT);
  assert.deepEqual(a, b);
  assert.deepEqual(dropModes(0.37, R, "metal", HIT), dropModes(0.37, R, "metal", HIT));
});
