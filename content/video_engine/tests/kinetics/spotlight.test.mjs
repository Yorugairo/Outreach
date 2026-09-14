// P57 T19 / R26-96 - THE SPOTLIGHT PROMOTED (the P55 T7 recipe). The promotion's proof is that every golden is
// byte-identical, so what this file pins is that the module still carries the INLINE ENGINE's numbers and
// arithmetic: the dials are the literals `paintSpecies sp.kind === "spotlight"` carried (SP.SPOT_DIM 0.49,
// SPOT_R_PORTRAIT 960 and the branch's own), the dim is the same four-stop curve, the hole glides between the
// same two declared targets on the same ease, and the idle is the same seeded breath and drift on the hole
// itself - E56's second half, the life check running on the addition's OWN region. How long a light holds is
// the COMPILER's (`dur: "hold"`, build_scene_timeline_f.py:4086-4094); the painter sees plain seconds, and
// this file checks that it does not start to have an opinion.
import { test } from "node:test";
import assert from "node:assert/strict";
import { SPOTLIGHT, spotlightGlide, spotlightIdle, spotlightCentre, spotlightRadius, spotlightGradient,
         spotlightStops, spotlightFade, paintSpotlight } from "../../scripts/species/spotlight.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const clamp = (v) => Math.min(1, Math.max(0, v));                        // the engine's clamp01, verbatim
const ease = (k) => 1 - Math.pow(1 - clamp(k), 3);                       // the engine's spEase, verbatim
const io = (k) => { k = clamp(k); return k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; };   // spIO
const STAGE = [1920, 1080];                                              // the engine's STAGE_W / STAGE_H
const BOX = { x: 400, y: 300, w: 800, h: 400 };                          // a declared region, in stage px
const DATUM = { x: 900, y: 500, w: 0, h: 0 };                            // a datum resolves to a POINT: w = 0
const centre = (b) => ({ cx: b.x + b.w / 2, cy: b.y + b.h / 2 });        // the engine's centre, verbatim
const STILL = { scale: 1, dx: 0, dy: 0 };
const FLAT = () => 0.5;                                                  // the hash at its middle

// ---------------------------------------------------------------- the dials, as the inline code carried them
test("every dial is the inline engine's literal, to the digit, and frozen", () => {
  assert.ok(Object.isFrozen(SPOTLIGHT));
  assert.equal(SPOTLIGHT.GLIDE_S, 0.6, "spIO((t - sp.at - (sp.glide_at || 0)) / 0.6)");
  assert.equal(SPOTLIGHT.IN_S, 0.4, "Math.min(spEase(k * dur / 0.4), spEase((1 - k) * dur / 0.4))");
  assert.equal(SPOTLIGHT.DIM, 0.49, "SP.SPOT_DIM - the operator's own number (2026-09-03)");
  assert.equal(SPOTLIGHT.FEATHER, 0.12, "(r0 + 0.12).toFixed(3)");
  assert.deepEqual([SPOTLIGHT.W_MIN, SPOTLIGHT.PAD], [240, 60], "Math.max(a.w, 240) / 2 + 60");
  assert.equal(SPOTLIGHT.R_PORTRAIT, 960, "SPOT_R_PORTRAIT - and the portrait gradient's own r");
  assert.equal(SPOTLIGHT.R_LANDSCAPE, 0.5, "the landscape gradient is objectBoundingBox: r 0.5");
  assert.equal(SPOTLIGHT.HASH_SALT, 991, "lpHash(seed | 0, si | 0, 991)");
  assert.equal(SPOTLIGHT.INK, "#000");
  assert.equal(SPOTLIGHT.R_PORTRAIT, STAGE[0] / 2, "the portrait radius IS the landscape half-width, kept on purpose");
});

test("how long a light holds is the compiler's, never the painter's", () => {
  const src = paintSpotlight.toString() + spotlightGlide.toString() + spotlightFade.toString();
  assert.ok(!/"hold"|'hold'|held/.test(src), "`dur: hold` is resolved before the player sees the row");
  assert.ok(!/Math\s*\.\s*random/.test(src), "the jitter's one source is the seeded hash");
});

// ---------------------------------------------------------------- the glide between the two declared targets
test("the glide starts at at + glide_at and takes GLIDE_S, on the io ease", () => {
  const sp = { kind: "spotlight", at: 6.0, glide_at: 3.0 };
  assert.equal(spotlightGlide(8.0, sp, io), 0, "before it begins the ease clamps to 0 - the `spotlight-hold` instant");
  assert.equal(spotlightGlide(9.0, sp, io), 0, "at the start exactly");
  assert.ok(near(spotlightGlide(9.3, sp, io), 0.5), "half way through GLIDE_S the io ease is exactly half");
  assert.equal(spotlightGlide(9.6, sp, io), 1, "landed - and it stays landed ...");
  assert.equal(spotlightGlide(14.0, sp, io), 1, "... at both PROOF_FRAMES instants");
  assert.ok(near(spotlightGlide(6.3, { at: 6.0 }, io), 0.5), "no glide_at: the glide begins at `at`");
});

test("the centre runs from one target's centre to the other's, and the idle drifts it", () => {
  const [a, z] = [centre(BOX), centre(DATUM)];
  assert.deepEqual(spotlightCentre(a, z, 0, STILL), { cx: a.cx, cy: a.cy }, "g 0 is the first target ...");
  assert.deepEqual(spotlightCentre(a, z, 1, STILL), { cx: z.cx, cy: z.cy }, "... g 1 the second, exactly");
  const half = spotlightCentre(a, z, 0.5, STILL);
  assert.ok(near(half.cx, (a.cx + z.cx) / 2) && near(half.cy, (a.cy + z.cy) / 2), "and it is linear in g");
  assert.deepEqual(spotlightCentre(a, a, 0.5, STILL), { cx: a.cx, cy: a.cy },
                   "no target2 resolves to the same target: the glide is a stillness, not a special case");
  const drifted = spotlightCentre(a, z, 0.5, { scale: 1, dx: 1.7, dy: -0.9 });
  assert.ok(near(drifted.cx - half.cx, 1.7) && near(drifted.cy - half.cy, -0.9), "the idle's offset is added last");
});

// ---------------------------------------------------------------- the hole, and its breath
test("the hole is the FIRST target's half-width plus PAD, over the gradient's radius", () => {
  assert.ok(near(spotlightRadius(BOX, STILL, false, STAGE[0]), (800 / 2 + 60) / 960));
  assert.ok(near(spotlightRadius(DATUM, STILL, false, STAGE[0]), (240 / 2 + 60) / 960),
            "a datum is a POINT (w = 0): W_MIN is the pool it still gets");
  assert.ok(near(spotlightRadius({ w: 100 }, STILL, false, STAGE[0]), (240 / 2 + 60) / 960), "... and so is anything under W_MIN");
  assert.equal(spotlightRadius(BOX, STILL, true, 1080), spotlightRadius(BOX, STILL, false, 1920),
               "PORTRAIT keeps the LANDSCAPE half-width as its divisor - the one number the portrait pass left alone");
});

test("the idle BREATHES the hole and DRIFTS it - the life check on the addition's own region (E49 / E56)", () => {
  const idle = (kind, t) => ({ breath: { scale: 1 + 0.012 * (1 - Math.cos(2 * Math.PI * 0.25 * t)) / 2, dx: 0, dy: 0 },
                               live: { scale: 1.012, dx: 2, dy: -1 } }[kind]);
  assert.deepEqual(spotlightIdle({ kind: "spotlight" }, 9, 0, idle), STILL, "no idle declared: still");
  assert.deepEqual(spotlightIdle({ idle: "none" }, 9, 0, idle), STILL, "`none` is DECLARED stillness - the same light");
  assert.deepEqual(spotlightIdle({ idle: "live" }, 9, 0, idle), { scale: 1.012, dx: 2, dy: -1 });
  const r = spotlightRadius(DATUM, { scale: 1.012 }, false, STAGE[0]), r1 = spotlightRadius(DATUM, STILL, false, STAGE[0]);
  assert.ok(near(r / r1, 1.012), "the radius is scaled by the idle's scale, and by nothing else");
  assert.notEqual(r.toFixed(3), r1.toFixed(3), "... by enough to move the stop the gradient writes: pixels shift");
});

test("the phase is seeded off the light's own salt, so two lights are never in step", () => {
  const seen = [];
  const idle = (kind, t, phase) => { seen.push(phase); return STILL; };
  spotlightIdle({ idle: "live" }, 9, 0.25, idle);
  assert.deepEqual(seen, [0.25], "the phase is handed straight through to the engine's idleXf");
});

// ---------------------------------------------------------------- the four stops, the gradient, the fade
test("the dim is FOUR stops: clear, clear at r0, DIM at the feather, DIM to the edge", () => {
  const s = spotlightStops(0.1875);
  assert.equal(s.length, 4);
  assert.deepEqual(s.map((x) => x.offset), [0, "0.188", "0.307", 1],
                   "r0 and r0 + FEATHER, to a thousandth - written by the same toFixed the inline code used");
  assert.deepEqual(s.map((x) => x["stop-opacity"]), [0, 0, SPOTLIGHT.DIM, SPOTLIGHT.DIM]);
  assert.ok(s.every((x) => x["stop-color"] === "#000"), "the dim is black taken away, never a colour laid over");
  assert.equal(s[0].offset, 0, "the stop at 0 is what makes the hole FLAT-clear and not a vignette");
});

test("the gradient: objectBoundingBox in landscape, userSpaceOnUse in portrait", () => {
  const land = spotlightGradient("spot0", 960, 540, false, ...STAGE);
  assert.deepEqual(land, { id: "spot0", cx: "0.5000", cy: "0.5000", r: 0.5 });
  const port = spotlightGradient("spot0", 540, 960, true, 1080, 1920);
  assert.deepEqual(port, { id: "spot0", gradientUnits: "userSpaceOnUse", cx: "540.0", cy: "960.0", r: 960 },
                   "a round hole the width of the short side, its offsets at their landscape size");
});

test("the fade is in over IN_S and out over IN_S, on the cubic ease", () => {
  assert.equal(spotlightFade(0, 24, ease), 0, "it comes up from nothing ...");
  assert.equal(spotlightFade(1, 24, ease), 0, "... and goes back to it");
  assert.ok(near(spotlightFade(SPOTLIGHT.IN_S / 24, 24, ease), 1), "in by IN_S, whatever dur is");
  assert.equal(spotlightFade((8.0 - 6.0) / 24, 24, ease), 1, "the `spotlight-hold` instant is fully up");
  assert.ok(near(spotlightFade(0.2 / 24 / 1, 24, ease), ease(0.5)), "half way in it is the ease at a half");
});

// ---------------------------------------------------------------- the painter, over a stub DOM
const stub = () => {
  const made = [];
  const el = (tag, cls, parent, attrs) => {
    const node = { tag, cls, parent, attrs: Object.assign({}, attrs) };
    made.push(node);
    return node;
  };
  return { made, el };
};

const ctxFor = (sp, t, s, o = {}) => Object.assign({
  sp, t, k: (t - sp.at) / (sp.dur || 1), dur: sp.dur || 1, si: 0, seed: 7, svg: "spSvg", el: s.el,
  resolveTarget: (tg) => (tg ? (tg.index === 191 ? DATUM : BOX) : null),
  centre, ease, io, idle: () => ({ scale: 1.012, dx: 2, dy: -1 }), hash: FLAT,
  STAGE_W: STAGE[0], STAGE_H: STAGE[1], PORTRAIT: false,
}, o);

test("no resolved target, nothing painted (the targeting law)", () => {
  const s = stub();
  paintSpotlight(Object.assign(ctxFor({ kind: "spotlight", at: 6, dur: 24 }, 8, s), { resolveTarget: () => null }));
  assert.equal(s.made.length, 0, "not even the defs: a species with no declared target does not fire");
});

test("held on its first datum: defs, gradient, four stops and ONE rect over the whole stage", () => {
  const s = stub();
  paintSpotlight(ctxFor({ kind: "spotlight", at: 6.0, dur: 24.0, idle: "live", glide_at: 3.0,
                          target: { kind: "datum", index: 60 }, target2: { kind: "datum", index: 191 } }, 8.0, s,
                        { idle: () => STILL }));
  assert.deepEqual(s.made.map((n) => n.tag), ["defs", "radialGradient", "stop", "stop", "stop", "stop", "rect"]);
  const [, rg, , , , , rect] = s.made;
  assert.deepEqual([rect.attrs.x, rect.attrs.y, rect.attrs.width, rect.attrs.height], [0, 0, 1920, 1080],
                   "the dim is the WHOLE frame; the light is the hole punched in it");
  assert.equal(rect.attrs.fill, "url(#spot0)");
  assert.equal(rect.attrs.opacity, "1.00", "fully up at the `spotlight-hold` instant");
  assert.equal(rg.attrs.cx, (centre(BOX).cx / 1920).toFixed(4), "g 0: still on `target`, no drift");
  assert.equal(rg.attrs.cy, (centre(BOX).cy / 1080).toFixed(4));
});

test("landed on target2, breathing: the same seven nodes, the centre and the radius moved", () => {
  const sp = { kind: "spotlight", at: 6.0, dur: 24.0, idle: "live", glide_at: 3.0,
               target: { kind: "datum", index: 60 }, target2: { kind: "datum", index: 191 } };
  const s = stub();
  paintSpotlight(ctxFor(sp, 12.0, s));
  const rg = s.made[1], stops = s.made.slice(2, 6);
  assert.equal(rg.attrs.cx, ((centre(DATUM).cx + 2) / 1920).toFixed(4), "the glide landed, then the idle drifted it");
  assert.equal(rg.attrs.cy, ((centre(DATUM).cy - 1) / 1080).toFixed(4));
  assert.equal(stops[1].attrs.offset, spotlightRadius(BOX, { scale: 1.012 }, false, 1920).toFixed(3),
               "the radius is the FIRST target's throughout: a light does not change size because it moved");
  const still = stub();
  paintSpotlight(ctxFor(sp, 12.0, still, { idle: () => STILL }));
  assert.notEqual(still.made[1].attrs.cx, rg.attrs.cx, "and the idle is what makes the two proof frames differ");
  assert.notEqual(still.made[3].attrs.offset, stops[3].attrs.offset, "... and the breath is what moves the feather");
});

test("the id is the species' own index, so two lights in one scene never share a gradient", () => {
  const sp = { kind: "spotlight", at: 6.0, dur: 24.0, target: { kind: "point" } };
  const s = stub();
  paintSpotlight(ctxFor(sp, 12.0, s, { si: 3 }));
  assert.equal(s.made[1].attrs.id, "spot3");
  assert.equal(s.made[6].attrs.fill, "url(#spot3)");
});
