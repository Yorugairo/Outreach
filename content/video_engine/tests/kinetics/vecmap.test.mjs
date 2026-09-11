// P50 T5 - THE VECTOR MAP (the Bravos world map, shots 57-80). The map's whole geometry is ONE similarity per
// composition (mapFit) and everything else - where a light sits, where an arc leaves and lands, where a figure
// stamps - is that fit applied to SOURCED data. These tests pin the fit in BOTH aspects, the round trip through
// it, the arc's ends and its lift toward the pole, the light's ramp, and that the frame a species rides is the
// same one the world does (the camera's mapping is camCssFor's, to the bit).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { IDLE, idleXf } from "../../scripts/kinetics/idle.mjs";
import { springPop } from "../../scripts/kinetics/spring.mjs";
import {
  VECMAP, LIGHT, ARC, STAMP, STAMP_SIZES, mapData, focusBox, mapFit, mapPoint, mapInvert, fitXf, vmTarget,
  vmIdle, vmGroupXf, lightAlpha, arcFrac, arcCrossF, arcDim, arcBowSign, arcPath, arcHead, arcCrossPaths,
  stampPose, stampAt, stampClamp, vmScreen, worldFit,
} from "../../scripts/species/vecmap.mjs";

const MAP_PATH = fileURLToPath(new URL("../../assets/maps/world-110m.paths.json", import.meta.url));
const RAW = readFileSync(MAP_PATH, "utf-8");
const DATA = mapData(RAW);
const LAND = [1920, 1080], PORT = [1080, 1920];   // the two stages the player is instantiated at
const FOCUS = ["IRN", "USA", "CHN"];              // the composition of shots 57-80
const bboxes = (ids) => ids.map((id) => DATA.countries[id].bbox);
const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the map parses once and is memoised by the asset string itself", () => {
  assert.ok(DATA && DATA.countries && Array.isArray(DATA.box));
  assert.deepEqual(DATA.box, [1000, 500]);
  assert.equal(Object.keys(DATA.countries).length, 177);
  assert.equal(mapData(RAW), DATA, "the same asset parses ONCE - 187 KB per frame would be the one slow thing here");
  assert.equal(mapData(""), null);
  assert.equal(mapData("{not json"), null);
});

test("the dials are the map's, and every clock is a real window", () => {
  assert.equal(LIGHT.IN_S, 0.3, "the plan's number: the fill rises over 0.3 s");
  assert.ok(LIGHT.MAX > 0 && LIGHT.MAX < 1, "a light is a LIGHT on the land, never a solid shape replacing it");
  assert.ok(ARC.DRAW_S > 0 && ARC.CROSS_S > 0 && STAMP.IN_S > 0);
  assert.ok(ARC.ENTER_K !== 1, "the two turns are UNEQUAL: equal ones give a circular arc and waste the fitter");
  assert.ok(ARC.DIM > 0 && ARC.DIM < 1, "a CUT flow dims; it does not vanish - it happened");
  assert.ok(STAMP_SIZES.year < STAMP_SIZES.figure, "a year is furniture: the same stamp, one size down");
  assert.ok(VECMAP.ZOOM_MAX > 1);
});

// ---------------------------------------------------------------- THE FIT, in both aspects
const inside = (fit, box, [W, H]) => {
  const m = VECMAP.MARGIN * Math.min(W, H) - 0.001;
  const a = mapPoint(fit, [box.x, box.y]), b = mapPoint(fit, [box.x + box.w, box.y + box.h]);
  return a.x >= m && a.y >= m && b.x <= W - m && b.y <= H - m;
};

test("the focus set's box sits inside the stage, with its margin, in BOTH aspects", () => {
  for (const [W, H] of [LAND, PORT]) {
    const fit = mapFit(DATA.box, bboxes(FOCUS), W, H);
    assert.ok(near(fit.sx, fit.sy), "ONE similarity: a map that stretches lies about distances");
    assert.ok(inside(fit, fit.box, [W, H]), `the framed box is not inside the ${W}x${H} stage`);
    // ... and every framed country's own bbox is inside it too - the padded union is what the fit contains
    for (const id of FOCUS) {
      const bb = DATA.countries[id].bbox;
      assert.ok(inside(fit, { x: bb[0], y: bb[1], w: bb[2] - bb[0], h: bb[3] - bb[1] }, [W, H]), `${id} is cut by the margin`);
    }
  }
});

test("no focus set frames the WHOLE world, letterboxed on 16:9 and fit to the width on 9:16", () => {
  const whole = mapFit(DATA.box, [], LAND[0], LAND[1]);
  assert.deepEqual([whole.box.x, whole.box.y, whole.box.w, whole.box.h], [0, 0, 1000, 500]);
  assert.ok(inside(whole, whole.box, LAND));
  const m = VECMAP.MARGIN * Math.min(LAND[0], LAND[1]);
  assert.ok(near(whole.sx, Math.min((LAND[0] - 2 * m) / 1000, (LAND[1] - 2 * m) / 500), 1e-12), "16:9 CONTAINS the box");
  const port = mapFit(DATA.box, bboxes(FOCUS), PORT[0], PORT[1]);
  const pm = VECMAP.MARGIN * Math.min(PORT[0], PORT[1]);
  assert.ok(near(port.sx, (PORT[0] - 2 * pm) / port.box.w, 1e-12),
    "a focus set is wider than it is tall, so CONTAIN on 9:16 IS fit to the width");
  assert.ok(port.sx > mapFit(DATA.box, [], PORT[0], PORT[1]).sx,
    "framing three countries on a phone shows them bigger than the whole world does on the same stage");
});

test("a focus set of one small country is capped by ZOOM_MAX - past it the world is a blob", () => {
  const fit = mapFit(DATA.box, bboxes(["TWN"]), LAND[0], LAND[1]);
  assert.equal(fit.sx, VECMAP.ZOOM_MAX);
  assert.ok(inside(fit, { x: DATA.countries.TWN.bbox[0], y: DATA.countries.TWN.bbox[1], w: 0, h: 0 }, LAND),
    "capped or not, the country it frames is on the stage");
});

test("the framed box is the focus set's bboxes unioned and padded, never one of them", () => {
  const f = focusBox(DATA.box, bboxes(FOCUS));
  const xs = bboxes(FOCUS).map((b) => b[0]), xe = bboxes(FOCUS).map((b) => b[2]);
  assert.ok(near(f.x, Math.min(...xs) - VECMAP.PAD));
  assert.ok(near(f.x + f.w, Math.max(...xe) + VECMAP.PAD));
  assert.deepEqual(focusBox(DATA.box, []), { x: 0, y: 0, w: 1000, h: 500 });
  assert.deepEqual(focusBox(DATA.box, [null, 7]), { x: 0, y: 0, w: 1000, h: 500 }, "a bbox that is not one is not a frame");
});

// ---------------------------------------------------------------- the round trip and the targets
test("mapPoint round-trips a centroid through the fit, in both aspects", () => {
  for (const [W, H] of [LAND, PORT]) {
    const fit = mapFit(DATA.box, bboxes(FOCUS), W, H);
    for (const id of FOCUS) {
      const c = DATA.countries[id].centroid, back = mapInvert(fit, mapPoint(fit, c));
      assert.ok(near(back[0], c[0], 1e-9) && near(back[1], c[1], 1e-9), `${id} did not survive the round trip`);
    }
    const q = mapPoint(fit, [0, 0]);
    assert.ok(near(q.x, fit.tx) && near(q.y, fit.ty), "the origin maps to the translation");
    assert.equal(fitXf(fit), "translate(" + fit.tx.toFixed(2) + " " + fit.ty.toFixed(2) + ") scale(" + fit.sx.toFixed(5) + ")");
  }
});

test("a target resolves to a place in MAP units: a country to its centroid, a map point to itself", () => {
  assert.deepEqual(vmTarget(DATA, { kind: "country", id: "IRN" }), DATA.countries.IRN.centroid);
  assert.deepEqual(vmTarget(DATA, { kind: "mappoint", x: 640, y: 168 }), [640, 168]);
  assert.equal(vmTarget(DATA, { kind: "country", id: "ATLANTIS" }), null, "a name that is not a place paints nothing");
  assert.equal(vmTarget(DATA, { kind: "point", x: 0.5, y: 0.5 }), null, "a STAGE point is not a place on the map");
  assert.equal(vmTarget(null, { kind: "country", id: "IRN" }), null);
});

// ---------------------------------------------------------------- THE LIGHT
test("the light rises over IN_S, holds at MAX, and leaves over OUT_S", () => {
  const at = 5, dur = 6;
  assert.equal(lightAlpha(at - 0.01, at, dur), 0, "nothing before its word");
  assert.equal(lightAlpha(at + dur + 0.01, at, dur), 0, "nothing after its window");
  assert.ok(near(lightAlpha(at, at, dur), 0), "it rises from nothing: never a pop");
  assert.ok(near(lightAlpha(at + LIGHT.IN_S / 2, at, dur), LIGHT.MAX / 2), "the ramp is linear in its own clock");
  for (const t of [at + LIGHT.IN_S, at + 2, at + dur - LIGHT.OUT_S]) {
    assert.ok(near(lightAlpha(t, at, dur), LIGHT.MAX), `the light HOLDS at ${t}`);
  }
  assert.ok(near(lightAlpha(at + dur - LIGHT.OUT_S / 2, at, dur), LIGHT.MAX / 2), "and leaves on its own clock");
  let last = -1, rising = true;   // monotone up then down: a light never flickers
  for (let i = 0; i <= 200; i++) {
    const a = lightAlpha(at + dur * i / 200, at, dur);
    if (a < last - 1e-12) rising = false;
    assert.ok(rising || a <= last + 1e-12, "the light flickered");
    last = a;
  }
});

test("the idle breathes the FILL, not the shape - a country cannot scale off its own outline", () => {
  const at = 5, dur = 6, peak = 1 + IDLE.BREATH_AMP;
  const still = lightAlpha(at + 2, at, dur, 1), breathed = lightAlpha(at + 2, at, dur, peak);
  assert.ok(breathed > still, "a held light that is bit-identical frame to frame is the defect E49 names");
  assert.ok(near(breathed, still * (1 + IDLE.BREATH_AMP * LIGHT.BREATH_K)));
  assert.ok(breathed / still < 1.15, "the breath is a breath, never a strobe");
});

// ---------------------------------------------------------------- THE ARC
test("the arc's samples start and end at the two centroids", () => {
  const fit = mapFit(DATA.box, bboxes(FOCUS), LAND[0], LAND[1]);
  const from = DATA.countries.IRN.centroid, to = DATA.countries.USA.centroid;
  const arc = arcPath(fit, from, to, ARC.BOW, arcBowSign(DATA.box, from, to));
  const a = mapPoint(fit, from), b = mapPoint(fit, to);
  assert.equal(arc.pts.length, ARC.SAMPLES);
  assert.ok(near(arc.pts[0].x, a.x, 1e-6) && near(arc.pts[0].y, a.y, 1e-6), "it leaves the place it names");
  const end = arc.pts[arc.pts.length - 1];
  assert.ok(near(end.x, b.x, 1e-4) && near(end.y, b.y, 1e-4), "and lands on the other");
  assert.ok(arc.d.startsWith("M") && arc.d.includes("L"), "the nib is handed a polyline, drawn BY LENGTH");
});

test("the bow lifts toward the POLE: a Gulf -> US arc rises over the chord, and a southern pair sags the other way", () => {
  const fit = mapFit(DATA.box, bboxes(FOCUS), LAND[0], LAND[1]);
  const gulf = [640, 168], usa = DATA.countries.USA.centroid;   // shots 57-64: the oil leaves the Gulf and crosses
  assert.equal(arcBowSign(DATA.box, gulf, usa), 1, "a WESTWARD flow in the north turns the other way to rise (the sign follows the run)");
  assert.equal(arcBowSign(DATA.box, usa, gulf), -1, "... and its eastward twin takes the opposite turn, for the same lift");
  const arc = arcPath(fit, gulf, usa, ARC.BOW, arcBowSign(DATA.box, gulf, usa));
  const p0 = arc.pts[0], p1 = arc.pts[arc.pts.length - 1];
  const chordY = (x) => p0.y + (p1.y - p0.y) * (x - p0.x) / (p1.x - p0.x);
  const lift = Math.max(...arc.pts.map((p) => chordY(p.x) - p.y));
  assert.ok(lift > 20, `the arc did not lift off its chord (max ${lift.toFixed(1)} px)`);
  assert.ok(arc.mid.y < chordY(arc.mid.x), "its midpoint - where the X is struck - is above the chord");
  // the southern twin: two places below the equator lift the other way, toward the south pole
  const za = DATA.countries.ZAF.centroid, ar = DATA.countries.ARG.centroid;
  assert.equal(arcBowSign(DATA.box, za, ar), -1, "a southern pair running west: the mirror of the northern westward arc");
  const south = arcPath(fit, za, ar, ARC.BOW, arcBowSign(DATA.box, za, ar));
  const sChord = (x) => south.pts[0].y + (south.pts[south.pts.length - 1].y - south.pts[0].y) * (x - south.pts[0].x) / (south.pts[south.pts.length - 1].x - south.pts[0].x);
  assert.ok(south.mid.y > sChord(south.mid.x), "a southern flow bows toward ITS pole");
});

test("the arc draws by its own clock, is cut on a LATER word, and dims under its X", () => {
  const sp = { kind: "arc", at: 4, dur: 8, crossed: 9 };
  assert.equal(arcFrac(sp, 3.9), 0);
  assert.ok(near(arcFrac(sp, 4 + ARC.DRAW_S / 2), 0.5));
  assert.equal(arcFrac(sp, 40), 1);
  assert.equal(arcCrossF(sp, 8.9), 0, "nothing is struck before the word that cuts the flow");
  assert.ok(near(arcCrossF(sp, 9 + ARC.CROSS_S / 2), 0.5));
  assert.equal(arcCrossF({ at: 4, dur: 8 }, 40), 0, "an arc with no `crossed` is never struck");
  assert.equal(arcDim(0), 1);
  assert.ok(near(arcDim(1), ARC.DIM));
  const [d0, d1] = arcCrossPaths({ x: 100, y: 200 }, 10);
  assert.equal(d0, "M90.0 190.0 L110.0 210.0");
  assert.equal(d1, "M110.0 190.0 L90.0 210.0");
});

test("the arrowhead sits on the tangent the arc arrives on", () => {
  const head = arcHead([{ x: 0, y: 0 }, { x: 100, y: 0 }]);
  assert.ok(head.includes("L100.00 0.00"), "the head's point IS the arc's end");
  const arms = head.match(/-?\d+\.\d+/g).map(Number);
  assert.ok(arms[0] < 100 && arms[4] < 100, "both arms trail behind the tip");
  assert.ok(near(arms[1], -arms[5], 1e-9), "and are symmetric about it");
  assert.equal(arcHead([{ x: 1, y: 1 }]), "", "one point is not an arrival");
});

// ---------------------------------------------------------------- THE STAMP
test("the stamp lands on the badge spring, at the size its `size` field names", () => {
  const sp = { kind: "stamp", at: 6, dur: 5, text: "1.4 Billion Barrels" };
  assert.equal(stampPose(sp, 5.9).fade, 0);
  assert.equal(stampPose(sp, 6).u, 0);
  assert.ok(near(stampPose(sp, 6 + STAMP.IN_S / 2).scale, STAMP.POP_FROM + (1 - STAMP.POP_FROM) * springPop(0.5)),
    "the landing IS springPop - a chip, a year stamp and a figure land alike");
  assert.equal(stampPose(sp, 6).scale, STAMP.POP_FROM, "it springs UP to its size: never a pop out of nothing");
  const rest = stampPose(sp, 20);
  assert.ok(near(rest.scale, 1, 1e-3) && near(rest.dy, STAMP.DY, 0.05), "it settles ON its place");
  assert.equal(rest.px, STAMP.FIGURE_PX);
  assert.equal(stampPose({ ...sp, size: "year" }, 20).px, STAMP.YEAR_PX);
  assert.equal(stampPose({ ...sp, size: "nonsense" }, 20).px, STAMP.FIGURE_PX, "an unknown size is the figure, never nothing");
  const fit = mapFit(DATA.box, bboxes(FOCUS), LAND[0], LAND[1]);
  assert.deepEqual(stampAt(fit, DATA.countries.CHN.centroid), mapPoint(fit, DATA.countries.CHN.centroid));
});

test("the type is placed at the screen point its place maps to, and kept ON the frame", () => {
  // vmScreen is the numeric twin of the transform vmGroupXf writes: the idle about the centre, then the camera
  const cam = { s: 2, ox: 400, oy: 300, ax: 960, ay: 540 }, ix = { scale: 1.01, dx: 2, dy: -1 };
  const p = { x: 500, y: 400 };
  const q0 = vmScreen(null, ix, p, 1920, 1080);
  assert.ok(near(q0.x, 960 + 2 + (500 - 960) * 1.01) && near(q0.y, 540 - 1 + (400 - 540) * 1.01));
  const q1 = vmScreen(cam, null, p, 1920, 1080);
  assert.ok(near(q1.x, 960 + 2 * (500 - 400)) && near(q1.y, 540 + 2 * (400 - 300)));
  assert.deepEqual(vmScreen(null, null, p, 1920, 1080), p, "no camera and no idle move nothing");
  const both = vmScreen(cam, ix, p, 1920, 1080), mid = vmScreen(null, ix, p, 1920, 1080);
  assert.deepEqual(both, vmScreen(cam, null, mid, 1920, 1080), "the order is the transform list's: the idle first, then the camera");
  // the clamp: a place at the frame's edge keeps its whole figure on the stage (China's centroid, 9:16)
  const wide = stampClamp({ x: 1070, y: 900 }, "1.4 Billion Barrels", STAMP.FIGURE_PX, PORT[0], PORT[1]);
  const half = "1.4 Billion Barrels".length * STAMP.FIGURE_PX * STAMP.CHAR_W / 2;
  assert.ok(near(wide.x, PORT[0] - STAMP.EDGE - half), "pushed in by its own half width");
  assert.equal(stampClamp({ x: 540, y: 900 }, "1996", STAMP.YEAR_PX, PORT[0], PORT[1]).x, 540, "a figure with room is not moved");
  assert.equal(stampClamp({ x: 10, y: 5 }, "1996", STAMP.YEAR_PX, PORT[0], PORT[1]).y, STAMP.EDGE + STAMP.YEAR_PX, "and the top edge is a floor too");
  const huge = stampClamp({ x: 10, y: 900 }, "x".repeat(200), STAMP.FIGURE_PX, PORT[0], PORT[1]);
  assert.equal(huge.x, PORT[0] / 2, "a figure wider than the stage stays centred - that one is the author's");
});

// ---------------------------------------------------------------- THE FRAME EVERY PAINTER RIDES
test("the world's fit is the one the species read - the same declaration, the same numbers", () => {
  const world = { kind: "vecmap", map: "world-110m", focus: FOCUS };
  for (const [W, H] of [LAND, PORT]) {
    assert.deepEqual(worldFit(DATA, world, W, H), mapFit(DATA.box, bboxes(FOCUS), W, H));
  }
  assert.equal(worldFit(null, world, 100, 100), null);
  assert.deepEqual(worldFit(DATA, { focus: ["NOWHERE"] }, LAND[0], LAND[1]), mapFit(DATA.box, [], LAND[0], LAND[1]),
    "a focus id the data does not carry frames the whole world rather than nothing");
});

test("the camera's mapping is camCssFor's - screen = at + s (p - look)", () => {
  assert.equal(vmGroupXf(null, { scale: 1, dx: 0, dy: 0 }, 1920, 1080), "", "identity writes nothing");
  assert.equal(vmGroupXf({ s: 1, ox: 100, oy: 100, ax: 100, ay: 100 }, null, 1920, 1080), "");
  const cam = { s: 2, ox: 400, oy: 300, ax: 960, ay: 540 };
  const xf = vmGroupXf(cam, null, 1920, 1080);
  assert.equal(xf, "translate(160.00 -60.00) scale(2.00000)");
  const p = { x: 400, y: 300 };   // the look point must land ON the screen point the key names
  assert.ok(near(160 + 2 * p.x, cam.ax) && near(-60 + 2 * p.y, cam.ay));
});

test("the idle is the WORLD's - the same kind, the same phase, so a light cannot slide off its country", () => {
  const scene = { span: [4, 12] }, world = { kind: "vecmap", idle: "breath" };
  const hash = (a, b, c) => ((a * 31 + b * 7 + c) % 97) / 97;
  const a = vmIdle(scene, world, 6.5, idleXf, hash);
  assert.deepEqual(a, idleXf("breath", 6.5, hash(Math.round(4 * 100), 0, 977)));
  assert.deepEqual(vmIdle(scene, { idle: "none" }, 6.5, idleXf, hash), { scale: 1, dx: 0, dy: 0 });
  assert.deepEqual(vmIdle(scene, {}, 6.5, idleXf, hash), idleXf(VECMAP.IDLE, 6.5, hash(400, 0, 977)),
    "a world that names no idle takes the plate's default (E49: nothing ever goes truly still)");
  // the player's idleOf carries the kinetics flag and the class default: when it says none, the map holds still
  assert.deepEqual(vmIdle(scene, world, 6.5, idleXf, hash, () => "none"), { scale: 1, dx: 0, dy: 0 });
  const ix = { scale: 1.01, dx: 2, dy: -1 };
  assert.equal(vmGroupXf(null, ix, 1000, 500), "translate(502.00 249.00) scale(1.01000) translate(-500.00 -250.00)");
});
