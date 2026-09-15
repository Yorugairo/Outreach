// P57 R26-118 / E88 s7 ("a more living ball, that is wriggling to contain itself, and has real, metallic mass and
// density") - THE LIVING DROP. These pin the four claims the header makes: the ring's AREA is pi R^2 at any t (the
// drop is incompressible - it wobbles, it never grows), mode l has exactly l lobes, the impulse's amplitude decays by
// exp(-t / tau) on Lamb's modulus, and the FLOOR (E49) never lets the surface come to rest. Plus the purity every
// scrubbed frame is built on: the same t twice is the same ring, vertex for vertex.
import { test } from "node:test";
import assert from "node:assert/strict";
import { DROP, dropOmega, dropTau, dropAmp, dropModes, dropRadius, dropArea, dropRing, dropSpecular, dropRimAlpha, dropBandAlpha, dropPitAlpha, dropDeepPoint, dropLightAxis }
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

// ---- P61 T5 / E99 s3: THE BALL'S SHADOWS ------------------------------------------------------------------------
// The operator (OPERATOR-RULINGS.md:2922-2925): "We definitely need more shadows. The shadows are where the
// weight/mass largely come from i think, dark fresnel rim + metallic band and I imagine incorporating at least one
// point of deep shadow depth." These pin the MATERIAL's three profiles: the rim DARKENS monotonically toward the
// silhouette (never a bright ring), the band is a stripe normal to the light with one peak, and the deep point is
// seated OPPOSITE the light and falls off monotonically. The paint they become is species/melt.mjs's, checked by
// tests/test_ball_material.py.

test("the shadow dials are frozen, declared, and carry their measured defaults", () => {
  assert.equal(Object.isFrozen(DROP), true);
  // (b) the dark grazing rim, (c) the metallic band, (d) the point of deep shadow depth - every one a NAMED dial
  for (const k of ["RIM_AT", "RIM_GAMMA", "RIM_A", "BAND_P", "BAND_H", "BAND_A", "PIT_AT", "PIT_R", "PIT_GAMMA", "PIT_A"]) {
    assert.ok(Number.isFinite(DROP[k]), `${k} is not a number`);
  }
  // the rim may START inside the specular seat (RIM_AT 0.42 against HL_AT 0.46) - what must hold is that it is
  // still NEGLIGIBLE there, or a wider rim would swallow the one highlight the metal reads by
  assert.ok(dropRimAlpha(DROP.HL_AT) < 0.05 * DROP.RIM_A,
    `the rim darkens the specular seat: ${dropRimAlpha(DROP.HL_AT)} of ${DROP.RIM_A}`);
  assert.ok(DROP.BAND_A < 1 && DROP.BAND_A > 0, "the band is a sheen, not an opaque decal");
});

test("the DARK grazing rim: zero inside RIM_AT, MONOTONE toward the silhouette, darkest AT it", () => {
  assert.equal(dropRimAlpha(0), 0);
  assert.equal(dropRimAlpha(DROP.RIM_AT), 0, "nothing inside the band's start");
  assert.ok(dropRimAlpha(DROP.RIM_AT - 0.01) === 0, "and nothing just inside it either");
  let prev = -1;
  for (let i = 0; i <= 400; i++) {
    const a = dropRimAlpha(i / 400);
    assert.ok(a >= prev - 1e-12, `not monotone at s=${i / 400}: ${a} after ${prev}`);
    assert.ok(a >= 0 && a <= 1, `alpha out of range at s=${i / 400}: ${a}`);
    prev = a;
  }
  near(dropRimAlpha(1), DROP.RIM_A, 1e-12, "at the silhouette");
  // it is a RIM and not a vignette: the outer tenth of the radius carries most of the darkening
  assert.ok(dropRimAlpha(0.9) < 0.5 * DROP.RIM_A, "the rim turns on late");
  assert.ok(dropRimAlpha(1) - dropRimAlpha(0.9) > dropRimAlpha(0.9) - dropRimAlpha(0.5), "most of it is the last tenth");
  // s is clamped: a wobble that pushes a sample past the nominal radius does not overshoot
  assert.equal(dropRimAlpha(1.4), dropRimAlpha(1));
});

test("the METALLIC BAND: one peak at BAND_P, normal to the light, falling away either side", () => {
  near(dropBandAlpha(DROP.BAND_P), DROP.BAND_A, 1e-12, "the peak");
  let up = true, prev = dropBandAlpha(0), peaks = 0;
  for (let i = 1; i <= 500; i++) {
    const a = dropBandAlpha(i / 500);
    if (up && a < prev) { peaks++; up = false; }
    if (!up && a > prev + 1e-12) up = true;
    prev = a;
  }
  assert.equal(peaks, 1, "exactly one band, not a stripe pattern");
  assert.ok(dropBandAlpha(0) < 0.02 * DROP.BAND_A && dropBandAlpha(1) < 0.02 * DROP.BAND_A, "the poles are clear of it");
  // the axis it runs along IS the light's: the lit pole first, the dark pole second (dropLightAxis, in bbox units)
  const ax = dropLightAxis(), th = DROP.LIGHT_DEG * Math.PI / 180;
  near(ax.x1, 0.5 + 0.5 * Math.cos(th), 1e-12, "the lit pole x");
  near(ax.y1, 0.5 + 0.5 * Math.sin(th), 1e-12, "the lit pole y");
  near(ax.x2, 1 - ax.x1, 1e-12, "and the dark pole is opposite it");
  near(ax.y2, 1 - ax.y1, 1e-12, "and the dark pole is opposite it");
});

test("the POINT OF DEEP SHADOW DEPTH sits OPPOSITE the light and falls off monotonically", () => {
  const seat = dropDeepPoint([0, 0], R);
  const wrap = (a) => Math.atan2(Math.sin(a), Math.cos(a));
  near(wrap(Math.atan2(seat.y, seat.x)), wrap((DROP.LIGHT_DEG + 180) * Math.PI / 180), 1e-12, "the seat's bearing");
  near(Math.hypot(seat.x, seat.y) / R, DROP.PIT_AT, 1e-12, "how far out it sits");
  assert.ok(seat.r > 0 && seat.r < R, "the well is on the ball");
  // and it is on the OTHER side from the specular spot: the highlight and the well never share a hemisphere
  const hl = dropSpecular([0, 0], R, dropModes(0.2, R, "metal", HIT));
  assert.ok(hl.x * seat.x + hl.y * seat.y < 0, "the well is opposite the highlight");
  near(dropPitAlpha(0), DROP.PIT_A, 1e-12, "deepest at the seat");
  assert.equal(dropPitAlpha(1), 0, "and gone at its reach");
  let prev = 2;
  for (let i = 0; i <= 400; i++) {
    const a = dropPitAlpha(i / 400);
    assert.ok(a <= prev + 1e-12, `not monotone at s=${i / 400}`);
    prev = a;
  }
});

test("every shading profile is a PURE function of t: two reads at one instant are identical", () => {
  for (const t of [0, 0.083, 0.37, 1.6]) {
    const a = dropModes(t, R, "metal", HIT), b = dropModes(t, R, "metal", HIT);
    assert.deepEqual(a, b);
    // the rim rides the local radius, so the same modes give the same shading at the same theta
    const sa = dropRadius(0.7, a), sb = dropRadius(0.7, b);
    assert.equal(dropRimAlpha(sa), dropRimAlpha(sb));
    assert.deepEqual(dropDeepPoint([0, 0], R), dropDeepPoint([0, 0], R));
    assert.deepEqual(dropLightAxis(), dropLightAxis());
  }
});
