// P69 T49 - THE FREEZE BEAT (E99 s99: "a light that comes on as everything else STOPS is a punctuation beat - the
// freeze is the event"). On a word every idle, drift and ambient life on the stage holds for 0.4-1.2 s while ONE light
// comes on at a named datum, mark or prop; then life resumes. These tests pin the LIFE CLOCK (the frozen time taken out
// of t, a pure function of t), the windows the timeline declares, the light's pose, its form, and the painter reached
// only through ctx.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { FREEZE, freezeWindows, frozenBefore, lifeClock, sceneClock, frozenAt, freezePose, freezeForm,
         paintFreeze } from "../../scripts/species/freeze.mjs";
import { LIT } from "../../scripts/species/lit_stretch.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const sc = (span, species) => ({ scene_id: "s", span, species });
const fz = (at, dur, o = {}) => Object.assign({ kind: "freeze", at, dur, target: { kind: "datum", index: 3 } }, o);

test("the dials: the beat is 0.4-1.2 s, the light comes on fast and goes as life resumes, in the relight's sunflower", () => {
  assert.equal(FREEZE.MIN_S, 0.4);
  assert.equal(FREEZE.MAX_S, 1.2);
  assert.ok(FREEZE.ON_S > 0 && FREEZE.ON_S < FREEZE.MIN_S / 2, "the light comes ON - quick, never a slow fade");
  assert.ok(FREEZE.OFF_S > 0 && FREEZE.ON_S + FREEZE.OFF_S < FREEZE.MAX_S);
  assert.ok(FREEZE.RAMP_MAX > 0 && FREEZE.RAMP_MAX <= 0.25, "on the shortest beat the ramps still leave a held middle");
  assert.equal(FREEZE.COLOR, "#F5B72E", "the relight's sunflower (the engine's PS.RELIGHT_COL), the page's one light colour");
  const engine = readFileSync(new URL("../../../../docs/content-video-engine/samples/scene-evidence-engine.mjs", import.meta.url), "utf8");
  assert.ok(engine.split(/\r?\n/).some((l) => l.includes('RELIGHT_COL: "#F5B72E"')), "the mirror matches the engine's own literal");
});

// ---------------------------------------------------------------- the windows the timeline declares
test("freezeWindows reads every freeze on every scene, clipped to its scene, sorted and merged", () => {
  const scenes = [sc([0, 10], [fz(8, 1.0), { kind: "figure", at: 2, dur: 1 }]),
                  sc([10, 20], [fz(9.8, 0.6), fz(15, 0.8), fz(15.5, 1.0)]),
                  sc([20, 30], [fz(29.5, 1.2)])];
  assert.deepEqual(freezeWindows(scenes), [[8, 9], [10, 10.4], [15, 16.5], [29.5, 30]]);
  assert.deepEqual(freezeWindows([]), []);
  assert.deepEqual(freezeWindows([sc([0, 5], [{ kind: "spotlight", at: 1, dur: 2 }])]), [], "no freeze, no window");
  assert.deepEqual(freezeWindows([sc([0, 5], [fz(1, 0), fz(2, "x")])]), [], "a window with no length holds nothing");
  assert.ok(Object.isFrozen(freezeWindows(scenes)), "read once at mount, never written again");
});

// ---------------------------------------------------------------- the life clock
test("with no freeze the life clock IS t - the same number, so every build without one paints byte-identically", () => {
  for (const t of [0, 0.1, 3.3333333333, 11.9, 1e6]) {
    assert.ok(Object.is(lifeClock([], t), t));
    assert.ok(Object.is(sceneClock([], t, 4.2), t));
  }
});

test("the life clock stops inside a freeze, runs at speed outside it, and never jumps", () => {
  const ws = [[10, 10.8], [20, 21]];
  assert.equal(lifeClock(ws, 9), 9);
  assert.equal(lifeClock(ws, 10), 10);
  assert.ok(near(lifeClock(ws, 10.4), 10) && near(lifeClock(ws, 10.8), 10), "held for the whole beat");
  assert.ok(near(lifeClock(ws, 11), 10.2), "then it resumes where it stopped - continuous, a beat behind t");
  assert.ok(near(lifeClock(ws, 20.5), 19.2) && near(lifeClock(ws, 22), 20.2));
  assert.ok(near(frozenBefore(ws, 30), 1.8));
  let prev = -Infinity;
  for (let t = 8; t < 23; t += 0.01) {
    const v = lifeClock(ws, t);
    assert.ok(v >= prev - 1e-12, "never runs backwards");
    assert.ok(v - prev <= 0.01 + 1e-9 || prev === -Infinity, "never jumps forward");
    prev = v;
  }
});

test("a scene-local clock (Ken Burns, a clip) counts only the freezes after its own origin", () => {
  const ws = [[10, 10.8], [20, 21]];
  assert.ok(near(sceneClock(ws, 25, 15), 24), "a scene that starts at 15 lost only the second beat");
  assert.ok(near(sceneClock(ws, 15, 15), 15), "its origin is its origin");
  assert.ok(near(sceneClock(ws, 10.5, 10), 10), "a push that starts on the beat holds with it");
});

test("frozenAt is true across the beat and false at its end, where life resumes", () => {
  const ws = [[10, 10.8]];
  assert.equal(frozenAt(ws, 9.99), false);
  assert.equal(frozenAt(ws, 10), true);
  assert.equal(frozenAt(ws, 10.79), true);
  assert.equal(frozenAt(ws, 10.8), false);
  assert.equal(frozenAt([], 10), false);
});

// ---------------------------------------------------------------- the light
test("the light comes on as the beat starts, HOLDS still through its middle, and goes as life resumes", () => {
  const sp = fz(10, 0.8);
  assert.equal(freezePose(sp, 9.99).f, 0);
  assert.ok(freezePose(sp, 10.02).f > 0 && freezePose(sp, 10.02).f < 1, "coming on");
  const a = freezePose(sp, 10.2), b = freezePose(sp, 10.5);
  assert.equal(a.f, 1);
  assert.deepEqual(a, b, "the held middle is one pose: the light is part of the stopped frame, it does not breathe");
  assert.ok(freezePose(sp, 10.75).f < 1 && freezePose(sp, 10.75).f > 0, "going as life resumes");
  assert.equal(freezePose(sp, 10.8).f, 0);
  assert.equal(freezePose(sp, 11).f, 0);
  const short = fz(10, 0.4);   /* the shortest beat: each ramp is at most RAMP_MAX of it, so a middle still holds */
  assert.equal(freezePose(short, 10.2).f, 1);
});

test("the light's form follows what the target resolves to: a point is a lit point, a box is a lit edge", () => {
  const p = freezeForm({ x: 400, y: 300, w: 0, h: 0 });
  assert.equal(p.kind, "point");
  assert.ok(near(p.cx, 400) && near(p.cy, 300) && near(p.r, FREEZE.CORE_PX));
  assert.ok(near(p.glow, FREEZE.CORE_PX * LIT.GLOW_K / LIT.HEAD_K), "the lit stretch's comet head, standing still");
  const b = freezeForm({ x: 100, y: 200, w: 80, h: 300 });   /* a bar, a prop's box, a mark's box */
  assert.equal(b.kind, "box");
  assert.ok(near(b.x, 100 - FREEZE.PAD) && near(b.y, 200 - FREEZE.PAD) && near(b.w, 80 + 2 * FREEZE.PAD) && near(b.h, 300 + 2 * FREEZE.PAD));
  assert.equal(freezeForm(null), null);
});

// ---------------------------------------------------------------- the painter, through ctx
const recorder = (box) => {
  const made = [];
  const el = (tag, cls, parent, attrs = {}) => { const n = { tag, cls, parent, attrs: Object.assign({}, attrs), style: {} }; made.push(n); return n; };
  return { made, ctx: (sp, t) => ({ sp, t, svg: { tag: "svg" }, el, resolveTarget: () => box }) };
};

test("the painter lights a point on a datum and paints nothing without a resolved target or outside the beat", () => {
  const r = recorder({ x: 500, y: 400, w: 0, h: 0 });
  paintFreeze(r.ctx(fz(10, 0.8), 10.4));
  const g = r.made.find((n) => n.tag === "g"), dot = r.made.find((n) => n.tag === "circle");
  assert.ok(g && dot, r.made.map((n) => n.tag).join(","));
  assert.equal(g.attrs.opacity, "1.000");
  assert.equal(dot.attrs.fill, FREEZE.COLOR);
  assert.ok(String(dot.style.filter).startsWith("drop-shadow("), "the lit look: a halo, lpBloom's form");
  const none = recorder(null);
  paintFreeze(none.ctx(fz(10, 0.8), 10.4));
  assert.equal(none.made.length, 0, "the targeting law: no resolved target, nothing painted");
  const late = recorder({ x: 500, y: 400, w: 0, h: 0 });
  paintFreeze(late.ctx(fz(10, 0.8), 10.9));
  assert.equal(late.made.length, 0);
});

test("the painter lights a box as an edge, never a fill over the thing it names", () => {
  const r = recorder({ x: 100, y: 200, w: 80, h: 300 });
  paintFreeze(r.ctx(fz(10, 0.8), 10.4));
  const rect = r.made.find((n) => n.tag === "rect");
  assert.ok(rect, r.made.map((n) => n.tag).join(","));
  assert.equal(rect.attrs.fill, "none");
  assert.equal(rect.attrs.stroke, FREEZE.COLOR);
});

test("the module registers its painter in the STAGE registry and declares that space", () => {
  const src = readFileSync(new URL("../../scripts/species/freeze.mjs", import.meta.url), "utf8").split(/\r?\n/);
  assert.equal(src[0].trim(), "/* SPACE: stage */");
  assert.ok(src.some((l) => l.includes('if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.freeze = paintFreeze;')));
});
