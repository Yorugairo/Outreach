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
import { IDLE, drift, idleXf, idleDriftCss } from "../../scripts/kinetics/idle.mjs";

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
