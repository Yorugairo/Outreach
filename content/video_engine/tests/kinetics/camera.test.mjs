// P49 T1-T3 - the camera: the species envelopes unchanged, keys that lerp, a CSS string that is the player's own for a
// zoom in place, a frustum that inverts the projection, an in-frame test that knows a point from a box.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CAM, CAM_EASES, camEase, camIdentity, camSpeciesState, camKeyState, camCssFor, camFrustum, camInFrame, camProject } from "../../scripts/kinetics/camera.mjs";

const W = 1080, H = 1920;
const oldCss = (s, ox, oy) => s === 1 ? "" : "translate(" + (ox - W / 2).toFixed(1) + "px, " + (oy - H / 2).toFixed(1) + "px) scale(" + s.toFixed(4) + ") translate(" + (W / 2 - ox).toFixed(1) + "px, " + (H / 2 - oy).toFixed(1) + "px)";

test("the punch envelope is the player's: in over PUNCH_IN, a hold, out over PUNCH_OUT, 1.14 at the hold", () => {
  const c = [600, 900], dur = 2.0;
  assert.equal(camSpeciesState("punch", -0.1, c, dur), null);
  assert.equal(camSpeciesState("punch", 0, c, dur).s, 1);
  assert.ok(Math.abs(camSpeciesState("punch", 0.5, c, dur).s - CAM.PUNCH_SCALE) < 1e-12, "the hold");
  const inHalf = camSpeciesState("punch", (CAM.PUNCH_IN / dur) / 2, c, dur).s;
  assert.ok(inHalf > 1 && inHalf < CAM.PUNCH_SCALE);
  assert.ok(Math.abs(camSpeciesState("punch", 1, c, dur).s - 1) < 1e-12, "back to 1 at the end");
  assert.deepEqual(camSpeciesState("punch", 0.5, c, dur).look, c); assert.deepEqual(camSpeciesState("punch", 0.5, c, dur).at, c);
});

test("the focus zoom reaches FOCUS_SCALE at 1/1.8 of its clock and holds dead still; the pull-back opens at PULL_FROM", () => {
  const c = [400, 700];
  assert.ok(Math.abs(camSpeciesState("focus_zoom", 1 / 1.8, c, 2).s - CAM.FOCUS_SCALE) < 1e-12);
  assert.ok(Math.abs(camSpeciesState("focus_zoom", 0.9, c, 2).s - CAM.FOCUS_SCALE) < 1e-12);
  assert.ok(Math.abs(camSpeciesState("pull_back", 0, c, 2).s - CAM.PULL_FROM) < 1e-12);
  assert.ok(Math.abs(camSpeciesState("pull_back", 1, c, 2).s - 1) < 1e-12);
  assert.equal(camSpeciesState("wobble", 0.5, c, 2), null);
});

test("camCssFor a zoom in place is byte-identical to the string the player always wrote", () => {
  for (const [s, ox, oy] of [[1.14, 600, 900], [1.32, 123.4, 987.6], [1.9, 540, 960], [1, 10, 10]]) {
    assert.equal(camCssFor({ s, look: [ox, oy], at: [ox, oy] }, W, H), oldCss(s, ox, oy));
  }
});

test("a pan's CSS maps screen = at + s (p - look) under a centre origin", () => {
  const st = { s: 1.5, look: [700, 500], at: [540, 960] };
  const css = camCssFor(st, W, H);
  const m = css.match(/translate\(([-\d.]+)px, ([-\d.]+)px\) scale\(([\d.]+)\)/);
  assert.ok(m, css);
  const tx = +m[1], ty = +m[2], s = +m[3];
  const O = [W / 2, H / 2], p = [700, 500];
  const screen = [O[0] + s * (p[0] - O[0]) + tx, O[1] + s * (p[1] - O[1]) + ty];   // CSS with origin O: screen = O + s (p - O) + t
  assert.ok(Math.abs(screen[0] - 540) < 0.05 && Math.abs(screen[1] - 960) < 0.05, "the look point lands at `at`");
  assert.deepEqual(camProject(st, [800, 600]), [540 + 1.5 * 100, 960 + 1.5 * 100]);
});

test("keys: identity before the first, lerp by the arriving key's ease between, hold after the last", () => {
  const keys = [{ t: 2, zoom: 1, look: [540, 960] }, { t: 4, zoom: 1.5, look: [700, 500], at: [540, 960], ease: "linear" }];
  assert.deepEqual(camKeyState(keys, 1, W, H), camIdentity(W, H));
  const mid = camKeyState(keys, 3, W, H);
  assert.ok(Math.abs(mid.s - 1.25) < 1e-12); assert.deepEqual(mid.look, [620, 730]); assert.deepEqual(mid.at, [540, 960]);
  const end = camKeyState(keys, 9, W, H);
  assert.equal(end.s, 1.5); assert.deepEqual(end.look, [700, 500]);
  const held = camKeyState([{ t: 1, zoom: 1.2, look: [100, 100] }, { t: 3, zoom: 2, look: [300, 300], ease: "hold" }], 2.5, W, H);
  assert.equal(held.s, 1.2, "a hold segment keeps the previous key until its time");
  assert.deepEqual(camKeyState([], 5, W, H), camIdentity(W, H));
});

test("the frustum inverts the projection; a box is in, partly in, or out; a point is in or out", () => {
  const st = { s: 2, look: [540, 960], at: [540, 960] };
  const fr = camFrustum(st, W, H);
  assert.deepEqual([fr.x0, fr.y0, fr.x1, fr.y1], [270, 480, 810, 1440]);   // a 2x zoom in place sees the middle half
  assert.equal(camInFrame(fr, { x: 300, y: 500, w: 100, h: 100 }, 2).inside, true);
  assert.equal(camInFrame(fr, { x: 0, y: 0, w: 100, h: 100 }, 2).visible, 0);
  const part = camInFrame(fr, { x: 200, y: 480, w: 140, h: 100 }, 2);
  assert.ok(part.visible > 0.49 && part.visible < 0.51 && !part.inside);
  assert.equal(camInFrame(fr, { x: 540, y: 960, w: 0, h: 0 }).visible, 1, "a point inside");
  assert.equal(camInFrame(fr, { x: 10, y: 10, w: 0, h: 0 }).visible, 0, "a point outside");
  assert.deepEqual(camFrustum(camIdentity(W, H), W, H), { x0: 0, y0: 0, x1: W, y1: H });
  assert.deepEqual(CAM_EASES, ["cubic", "inout", "linear", "hold"]);   // the set the compiler mirrors (CAMERA_EASES)
});
