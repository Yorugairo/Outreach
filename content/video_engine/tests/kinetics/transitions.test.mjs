// P57 T23 / R26-100 - THE DIP PROMOTED, AND THE BOUNDARY CLOCK WITH IT (the P55 T7 recipe). The promotion's proof
// is that every golden is byte-identical; what this file pins is that the module carries the INLINE ENGINE's
// arithmetic - and above all THE LAW E47 s1 rules and the grouping decision the module's header records:
//   LINEAR. A plain ramp to black over the last DIP_S/2 and back over the first DIP_S/2, both halves reaching 1 at
//   the boundary. Every assertion below that reads "linear" would fail under any ease, which is the point: the
//   reference's dip is linear to the frame (doc 46 s46.5, all 35 of its dips measured).
//   ONE CLOCK, TWO RIDERS. `straddleSecs` is the only code the dip and the blur-zoom share, and both are pinned
//   through it here - that sharing is why they are one module and the arrive-on-the-cut transitions are not.
// The instants are the `dip-boundary` golden's own (FRAME_T 15.0, @proof-ramp 14.88), so the two frames the parent
// read are pinned here as numbers as well as pixels.
import { test } from "node:test";
import assert from "node:assert/strict";
import { DIP, exitName, exitSecs, straddleSecs, dipAlpha, dipVeilOpacity } from "../../scripts/kinetics/transitions.mjs";

const near = (a, b, eps = 1e-12) => Math.abs(a - b) <= eps;
const DIP_S = 0.47;        // the engine's dial, which stays in the engine (the module's header says why)
const BLURZOOM_S = 0.27;   // its twin, the other rider of the same clock
const A = 15.0, Z = 30.0;  // the `dip-boundary` golden's second scene: the boundary at 15.0
const SCENE = {}, NEXT = {};   // two neighbours - the clock only asks whether they exist

// ---------------------------------------------------------------- the dials, as the inline code carried them
test("the dials are frozen and are the inline engine's own numbers", () => {
  assert.ok(Object.isFrozen(DIP));
  assert.equal(DIP.HALVES, 2, "the engine's `dipOut / 2` and `dipIn / 2`: half the transition in each scene");
  assert.equal(DIP.OPACITY_DP, 4, "the engine's `dipA.toFixed(4)`");
  assert.deepEqual(Object.keys(DIP), ["HALVES", "OPACITY_DP"], "no dial was invented in the lift");
});

// ---------------------------------------------------------------- the exit grammar (verbatim from the engine)
test("exitName reads the name off the row and nothing else", () => {
  assert.equal(exitName("dip"), "dip");
  assert.equal(exitName("dip:0.8"), "dip");
  assert.equal(exitName("suck:0.5,0.5"), "suck");
  assert.equal(exitName("slide:left:0.9"), "slide");
  assert.equal(exitName(undefined), "", "a row with no exit names nothing - never a crash");
  assert.equal(exitName(null), "");
  assert.equal(exitName(7), "", "a non-string is not an exit");
});

test("exitSecs takes the row's declared seconds, else the caller's dial", () => {
  assert.equal(exitSecs("dip", DIP_S), DIP_S, "a bare dip leaves the player on DIP_S");
  assert.equal(exitSecs("dip:0.8", DIP_S), 0.8, "a timed dip runs for what it says");
  assert.equal(exitSecs("blurzoom:1.25", BLURZOOM_S), 1.25);
  assert.equal(exitSecs("dip:0", DIP_S), DIP_S, "zero is not a transition - the dial stands");
  assert.equal(exitSecs("dip:-2", DIP_S), DIP_S, "nor is a negative one");
  assert.equal(exitSecs("dip:soon", DIP_S), DIP_S, "nor is an unreadable suffix - the compiler refuses those");
  assert.equal(exitSecs(undefined, DIP_S), DIP_S);
});

// ---------------------------------------------------------------- THE STRADDLE CLOCK (the shared code)
test("the straddle clock gives each side its half, and 0 when the side has no neighbour", () => {
  assert.equal(straddleSecs(SCENE, "dip", "dip", DIP_S), DIP_S, "prev exists and this scene's exit says dip");
  assert.equal(straddleSecs(undefined, "dip", "dip", DIP_S), 0, "the FIRST scene has no incoming half");
  assert.equal(straddleSecs(NEXT, undefined, "dip", DIP_S), 0, "the LAST scene has no outgoing half (nxt && nxt.exit)");
  assert.equal(straddleSecs(SCENE, "cut", "dip", DIP_S), 0, "a cut is a cut");
  assert.equal(straddleSecs(SCENE, "blurzoom", "dip", DIP_S), 0, "another transition's row is not this one's");
  assert.equal(straddleSecs(SCENE, "dip:0.8", "dip", DIP_S), 0.8, "a timed dip carries its own seconds through the clock");
});

test("the blur-zoom rides the SAME clock - the one thing the two transitions share", () => {
  assert.equal(straddleSecs(SCENE, "blurzoom", "blurzoom", BLURZOOM_S), BLURZOOM_S);
  assert.equal(straddleSecs(SCENE, "blurzoom:0.4", "blurzoom", BLURZOOM_S), 0.4);
  assert.equal(straddleSecs(SCENE, "dip", "blurzoom", BLURZOOM_S), 0);
  assert.equal(straddleSecs(undefined, "blurzoom", "blurzoom", BLURZOOM_S), 0);
});

// ---------------------------------------------------------------- THE RAMP (E47 s1: LINEAR, and black on the boundary)
test("the boundary frame is BLACK from both sides - the cut happens inside it", () => {
  assert.equal(dipAlpha(A, A, Z, DIP_S, 0), 1, "the incoming half is at its deepest on the scene's first frame");
  assert.equal(dipAlpha(Z, A, Z, 0, DIP_S), 1, "the outgoing half is at its deepest on the boundary it runs into");
});

test("the ramp is LINEAR in t on both sides - no ease, by ruling", () => {
  for (const u of [0.25, 0.5, 0.75]) {
    const half = DIP_S / 2;
    assert.ok(near(dipAlpha(A + u * half, A, Z, DIP_S, 0), 1 - u), `the way up at u ${u}`);
    assert.ok(near(dipAlpha(Z - u * half, A, Z, 0, DIP_S), 1 - u), `the way down at u ${u}`);
  }
  // and the difference between equally spaced instants is constant, which only a straight line does
  const at = (t) => dipAlpha(t, A, Z, DIP_S, 0), s = DIP_S / 8;
  assert.ok(near(at(A + s) - at(A + 2 * s), at(A + 2 * s) - at(A + 3 * s)));
});

test("outside its own half-window the ramp is 0 - a whole DIP_S before the boundary the frame is untouched", () => {
  assert.equal(dipAlpha(Z - DIP_S, A, Z, 0, DIP_S), 0, "test_transitions_e47's own assertion, as a number");
  assert.equal(dipAlpha(A + DIP_S, A, Z, DIP_S, 0), 0);
  assert.equal(dipAlpha(20.0, A, Z, DIP_S, DIP_S), 0, "mid-scene, far from either boundary");
  assert.equal(dipAlpha(20.0, A, Z, 0, 0), 0, "a scene with no dip on either side is never dimmed");
});

test("both halves at once: the deeper black wins (Math.max, never a sum)", () => {
  const a = dipAlpha(A + DIP_S / 4, A, A + DIP_S / 2, DIP_S, DIP_S);   // a scene short enough to dip in and out at once
  assert.ok(a <= 1, "two ramps may never add past black");
  assert.ok(near(a, 0.5), "at the meeting point each half is exactly half way, so the max is 0.5");
});

test("a timed dip stretches the window and nothing else", () => {
  assert.ok(near(dipAlpha(A + 0.2, A, Z, 0.8, 0), 0.5), "dip:0.8 -> a 0.4 s half, half way at 0.2 s");
  assert.ok(near(dipAlpha(A + 0.2, A, Z, DIP_S, 0), 1 - 0.2 / (DIP_S / 2)), "the default's own half is steeper");
});

// ---------------------------------------------------------------- the two goldens, as numbers
test("the `dip-boundary` goldens' instants are these values", () => {
  assert.equal(dipAlpha(15.0, 15.0, 30.0, DIP_S, 0), 1, "frames/dip-boundary.png: the black boundary frame");
  const ramp = dipAlpha(14.88, 0.0, 15.0, 0, DIP_S);   // the OUTGOING scene, one scrub step off the ramp's midpoint
  assert.ok(near(ramp, 1 - 0.12 / (DIP_S / 2), 1e-9), "frames/dip-boundary@proof-ramp.png: just under half its light");
  assert.equal(dipVeilOpacity(ramp), "0.4894", "the veil's opacity string the engine writes at that frame");
});

test("the veil's opacity is the engine's toFixed(4), verbatim", () => {
  assert.equal(dipVeilOpacity(0), "0.0000");
  assert.equal(dipVeilOpacity(1), "1.0000");
  assert.equal(dipVeilOpacity(1 / 3), "0.3333");
  assert.equal(dipVeilOpacity(0.12345678), "0.1235", "four digits, rounded - an explicit numeric per frame");
});
