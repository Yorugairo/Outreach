// R26-133 - A PLATE'S `drift` IDLE PAINTS (E49; the operator, 2026-09-14: "Plate idle should probably paint, but
// would have to see what it looks like"). The defect: the player read a plate world's idle for its `.scale` alone,
// and `drift` is {scale: 1, dx, dy} - so a plate authored `;idle=drift` held perfectly still. The cure is the
// translation half of the pose, written into the world's rest term behind the `plate_idle_paints` dial, and shared
// per plane at its own depth k the way the camera's translation is shared.
//
// What is pinned here: (1) the pure law - the walk is bounded by DRIFT_PX, its scale is exactly 1, and two instants
// of one drift plate differ by at most 2 * DRIFT_PX on each axis; (2) the dial's two states - ON the world's rest
// term carries a translation, OFF (and for every idle whose dx/dy are zero) it is the identity string the engine
// has always written; (3) that the engine composes it at the world's rest term and at each plane.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { IDLE, drift, idleXf, idleDriftCss, idleDriftPx } from "../../scripts/kinetics/idle.mjs";

const ENGINE = fileURLToPath(new URL("../../../../docs/content-video-engine/samples/scene-evidence-engine.mjs", import.meta.url));

// what the engine writes for the world at parallax factor k: "" when the dial is off, the drift when it is on
const rest = (pose, on, k = 1) => "scale(1.0000) " + (on ? idleDriftCss(pose, k) : "");

test("a drift pose is scale 1 and a bounded walk - the reason reading `.scale` alone delivered nothing", () => {
  for (let i = 0; i <= 2000; i++) {
    const x = idleXf("drift", i / 50, 0.37);
    assert.equal(x.scale, 1, "drift never scales - this is why a `.scale`-only read held the plate still");
    assert.ok(Math.abs(x.dx) <= IDLE.DRIFT_PX + 1e-12, `dx ${x.dx}`);
    assert.ok(Math.abs(x.dy) <= IDLE.DRIFT_PX * 0.6 + 1e-12, `dy ${x.dy}`);
  }
  assert.deepEqual(drift(0, 0), [0, 0], "the walk opens at rest");
});

test("WITH the dial, two instants of a drift plate differ by at most 2 * DRIFT_PX on each axis", () => {
  const read = (t) => idleXf("drift", t, 0.37);
  let moved = false;
  for (let i = 0; i <= 1000; i++) {
    for (const dt of [0.0667, 1.0, 3.7, 11.3]) {
      const a = read(i / 20), b = read(i / 20 + dt);
      assert.ok(Math.abs(b.dx - a.dx) <= 2 * IDLE.DRIFT_PX + 1e-12, `dx shift ${b.dx - a.dx}`);
      assert.ok(Math.abs(b.dy - a.dy) <= 2 * IDLE.DRIFT_PX + 1e-12, `dy shift ${b.dy - a.dy}`);
      assert.equal(a.scale, 1);
      assert.equal(b.scale, 1);
      if (rest(a, true) !== rest(b, true)) moved = true;
    }
  }
  assert.ok(moved, "with the dial on, the world's rest term is not the same string at two instants");
});

test("WITHOUT the dial the rest term is the identity translation - byte-for-byte the string it always was", () => {
  for (let i = 0; i <= 200; i++) {
    const pose = idleXf("drift", i / 7, 0.37);
    assert.equal(rest(pose, false), "scale(1.0000) ", "the dial off writes no translation at all");
  }
  assert.equal(idleDriftCss({ scale: 1, dx: 0, dy: 0 }), "", "a pose that moves nothing writes nothing");
  assert.equal(idleDriftCss(idleXf("breath", 3.3, 0.2)), "", "a breath is a scale: it adds no translation here");
  assert.equal(idleDriftCss(idleXf("none", 3.3)), "", "`none` is the identity, to the string");
});

test("a plane takes the SHARE k of the same walk, clamped to the compiler's depth range", () => {
  const pose = idleXf("drift", 4.3, 0.37);
  const at = (k) => idleDriftCss(pose, k);
  const num = (s) => s.match(/-?\d+\.\d+/g).map(Number);
  const [x1, y1] = num(at(1));
  const [xn, yn] = num(at(1.4));                       // doc 24's `-near`
  assert.ok(Math.abs(xn) > Math.abs(x1) && Math.abs(yn) > Math.abs(y1), "the near plane drifts further than the flat wall");
  assert.deepEqual(num(at(1.4)), [+(pose.dx * 1.4).toFixed(2), +(pose.dy * 1.4).toFixed(2)]);
  assert.equal(at(0), "", "a plane pinned to the frame takes none of the walk");
  assert.deepEqual(num(at(99)), num(at(4)), "k is clamped at the compiler's ceiling, as the camera clamps it");
  assert.equal(at(-3), "", "a negative clamps to K_MIN, as the camera clamps it - it never inverts the plane");
  assert.deepEqual(num(at(NaN)), num(at(1)), "an unknown depth is the flat share, the camera's own rule for NaN");
  assert.equal(at(1), idleDriftCss(pose), "k defaults to the flat plate");
});

test("two seeks to one t write one string (fixed decimals, a pure function of t)", () => {
  for (let i = 0; i <= 500; i++) {
    const t = i / 13;
    assert.equal(idleDriftCss(idleXf("drift", t, 0.37), 1.15), idleDriftCss(idleXf("drift", t, 0.37), 1.15));
  }
});

test("the ENGINE composes it: at the world's rest term and at every plane, both behind the dial", () => {
  const src = readFileSync(ENGINE, "utf8");
  assert.match(src, /plate_idle_paints/, "the dial is declared in KINETICS_DIALS");
  assert.match(src, /const idleDrift = \(k\) => \(KIN\.plate_idle_paints === true \? idleDriftCss\(idlePose, k\) : ""\);/,
    "the world's paint block gates the drift on the dial");
  assert.match(src, /const restFlat = worldRest \+ idleDrift\(PARALLAX\.FLAT\);/,
    "the flat world's rest term carries the drift at k = 1");
  assert.match(src, /camCssAt\(xf, plies\[i\]\.k\) \+ rest \+ \(idleAt \? idleAt\(plies\[i\]\.k\) : ""\)/,
    "each plane carries the drift at its own share of it");
  assert.match(src, /const zi = idlePose\.scale;/, "the scale is still the world's `z` and is not written twice");
});

// ---- E99 s55: THE AMPLITUDE DIAL -------------------------------------------------------------
// The operator, 2026-09-16, on the three-way proof: "i think we need both the drift painted as an option and the
// alive ... maybe we need a slightly smaller drift (maybe 30 px?) AND the alive water. I think for youtube the 40 px
// drift would be too much motion fora long form, but it looks like it might work really well for shorts and certain
// scenes." So the walk gets a REAL amplitude, authored per scene, with the module constant as its floor.

test("the amplitude resolves row first, then the build's dial, then the module's own floor", () => {
  assert.equal(idleDriftPx(30, 40), 30, "the ROW outranks the build");
  assert.equal(idleDriftPx(undefined, 40), 40, "no row: the build's dial");
  assert.equal(idleDriftPx(undefined, undefined), IDLE.DRIFT_PX, "neither: the module constant - there is NO global default");
  assert.equal(idleDriftPx(null, ""), IDLE.DRIFT_PX, "an absent dial is absent however it arrives");
  assert.equal(idleDriftPx("30"), 30, "a number that came through JSON as a string still reads");
});

test("DRIFT_PX is a FLOOR, never a setting to go under - E49 cannot be switched off by a dial", () => {
  assert.equal(idleDriftPx(0.5), IDLE.DRIFT_PX, "under the floor is raised to it (the compiler refuses it by name)");
  assert.equal(idleDriftPx(-40), IDLE.DRIFT_PX, "a negative is not a drift in the other direction");
  assert.equal(idleDriftPx(NaN, "abc"), IDLE.DRIFT_PX, "nonsense falls through to the floor, never to zero");
  assert.equal(idleDriftPx(0), IDLE.DRIFT_PX, "zero is the one thing E49 forbids");
});

test("the amplitude sizes the walk and nothing else: the bound scales, the rates do not", () => {
  const AMP = 30;
  let maxDx = 0, maxDy = 0;
  for (let i = 0; i <= 4000; i++) {
    const a = idleXf("drift", i / 40, 0.37), b = idleXf("drift", i / 40, 0.37, { DRIFT_PX: AMP });
    assert.equal(b.scale, 1, "a bigger drift is still not a scale");
    assert.ok(Math.abs(b.dx - a.dx * AMP / IDLE.DRIFT_PX) < 1e-9, "x is the SAME walk, scaled");
    assert.ok(Math.abs(b.dy - a.dy * AMP / IDLE.DRIFT_PX) < 1e-9, "y likewise - so the drift can never become jitter");
    maxDx = Math.max(maxDx, Math.abs(b.dx)); maxDy = Math.max(maxDy, Math.abs(b.dy));
  }
  assert.ok(maxDx > AMP * 0.99 && maxDx <= AMP + 1e-9, `x reaches its bound: ${maxDx}`);
  assert.ok(maxDy > AMP * 0.6 * 0.99 && maxDy <= AMP * 0.6 + 1e-9, `y is 0.6 of it: ${maxDy}`);
});

test("at the ruled settings the walk is a motion the eye can see - E99 s38's own test", () => {
  // E99 s38: "8 frames to move 1 pixel is probably not even enough to realy register". At 30 fps, over one second.
  const step = (amp) => {
    let worst = 0;
    for (let i = 0; i < 300; i++) {
      const a = idleXf("drift", i / 30, 0.37, { DRIFT_PX: amp }), b = idleXf("drift", (i + 1) / 30, 0.37, { DRIFT_PX: amp });
      worst = Math.max(worst, Math.hypot(b.dx - a.dx, b.dy - a.dy));
    }
    return worst;
  };
  const floor = step(IDLE.DRIFT_PX), long = step(30), shorts = step(40);
  assert.ok(floor < 0.1, `the floor moves ${floor.toFixed(3)} px per frame - the invisible case E99 s38 refused`);
  assert.ok(long > 10 * floor, "30 px moves an order of magnitude further per frame than the floor");
  assert.ok(shorts > long, "40 px, the shorts setting, further still");
});

test("the ENGINE reads the amplitude at the plate's idle pose, row before build before the constant", () => {
  const src = readFileSync(ENGINE, "utf8");
  assert.match(src, /plate_idle_drift_px: "the plate idle drift's half-width in stage px/, "the dial is declared in KINETICS_DIALS");
  assert.match(src, /const idleAmp = idleDriftPx\(scene\.world\.idle_drift_px, KIN\.plate_idle_drift_px\);/,
    "the ROW's px is read before the build's dial, and the module's floor is behind both");
  assert.match(src, /idleXf\(idleOf\("plate", scene\.world\.idle\), t, lpHash\(Math\.round\(scene\.span\[0\] \* 100\), 0, 977\), \{ DRIFT_PX: idleAmp \}\)/,
    "the amplitude is threaded into the pose itself, so every reader of idlePose gets it");
  assert.ok(!/DRIFT_PX:\s*30/.test(src), "a second default in the engine is exactly the drift this pins");
});
