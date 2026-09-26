// P73 T5 - MAP POINTS. A place too small for the 110m outlines (Hong Kong, Singapore, Macau, Hsinchu) is a POINT the
// compiler resolved from the gazetteer (assets/maps/places.json) onto the target as {kind: "place", id, x, y, label}.
// These tests pin what the painter does with it: it is an arc's end and a stamp's place exactly as a mappoint is; a
// `light` on it paints a DOT and the place's NAME in the light's ink, on the light's own clock, in plain stage px (a
// camera zoom moves them with the place and never magnifies them - the stamp's rule), and `ping: true` fires T46d's
// one pulse at the point (paintPing, called - its body is T46d's). A country's light paints what it painted before.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { idleXf } from "../../scripts/kinetics/idle.mjs";
import {
  LIGHT, STAMP, PING, PLACE, mapData, mapFit, mapPoint, vmTarget, vmScreen, lightAlpha, pingAt, pingPose,
  PLACE_SIDES, placeLabelAt, placeDotStyle, placeLabelStyle, paintLight, paintArc, paintStamp, arcPath, arcBowSign,
} from "../../scripts/species/vecmap.mjs";

const RAW = readFileSync(fileURLToPath(new URL("../../assets/maps/world-110m.paths.json", import.meta.url)), "utf-8");
const PLACES = JSON.parse(readFileSync(fileURLToPath(new URL("../../assets/maps/places.json", import.meta.url)), "utf-8")).places;
const DATA = mapData(RAW);
const LAND = [1920, 1080];
const FOCUS = ["USA", "CHN"];
const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const hk = (extra = {}) => ({ kind: "place", id: "HKG", x: PLACES.HKG.x, y: PLACES.HKG.y, label: PLACES.HKG.label, ...extra });
const tightFit = () => mapFit(DATA.box, FOCUS.map((id) => DATA.countries[id].bbox), ...LAND, undefined, { tight: true });

const recorder = () => {
  const out = [];
  const el = (tag, cls, parent, attrs = {}) => { const n = { tag, cls, attrs, kids: [] }; (parent ? parent.kids : out).push(n); return n; };
  const flat = (ns) => ns.flatMap((n) => [n, ...flat(n.kids)]);
  return { out, el, all: () => flat(out) };
};
const ctx = (sp, t, rec, cam = null) => ({
  sp, t, svg: null, el: rec.el, drawOn: () => {}, sc: { span: [0, 30], world: { kind: "vecmap", map: "world-110m", focus: FOCUS, fit: "tight" } },
  A: { "map:world-110m": RAW }, camNow: cam ? () => cam : null, idle: idleXf, hash: () => 0, idleOf: null, seed: 1, si: 0,
  STAGE_W: LAND[0], STAGE_H: LAND[1],
});
const lightSp = (extra = {}) => ({ kind: "light", at: 5.9, dur: 10.0, target: hk(), ...extra });

test("a resolved place is a point in map units; an unresolved one is nothing", () => {
  assert.deepEqual(vmTarget(DATA, hk()), [PLACES.HKG.x, PLACES.HKG.y]);
  assert.equal(vmTarget(DATA, { kind: "place", id: "HKG" }), null, "the compiler resolves it - the player never guesses a point");
  assert.equal(vmTarget(DATA, { kind: "place", id: "HKG", x: null, y: 3 }), null);
});

test("the dials are stated, and the dot is smaller than the ping it leaves from", () => {
  assert.ok(PLACE.DOT_R > 0 && PLACE.DOT_R < PING.R0, "the pulse leaves the dot's edge, outside it");
  assert.ok(PLACE.LABEL_PX >= 28 && PLACE.LABEL_PX <= STAMP.YEAR_PX, "a name is a label: phone-legible, under a year's size");
  assert.ok(PLACE.POP_FROM > 0 && PLACE.POP_FROM < 1 && PLACE.GAP > 0 && PLACE.GLOW_PX > 0);
  assert.match(placeDotStyle(), /drop-shadow\(0 0 \d+(\.\d+)?px var\(--sunflower\)\)/, "a filled mark glows in its own ink (s130)");
  assert.match(placeDotStyle(), /^fill:var\(--sunflower\);/, "the dot is the light's ink");
  assert.match(placeLabelStyle(), /^font:600 30px Inter, Arial, sans-serif;fill:var\(--sunflower\);/, "the name is the light's ink, at LABEL_PX");
});

test("a light on a place paints ONE dot and ONE name at the point, on the light's clock, and no country", () => {
  const sp = lightSp(), t = sp.at + 1.0, rec = recorder();
  paintLight(ctx(sp, t, rec));
  const all = rec.all();
  const dots = all.filter((n) => n.cls === "vmplace"), names = all.filter((n) => n.cls === "vmplabel");
  assert.equal(dots.length, 1); assert.equal(names.length, 1);
  assert.deepEqual(all.filter((n) => n.cls === "vmlit"), [], "a place has no outline to fill");
  const q = vmScreen(null, idleXf("breath", t, 0), mapPoint(tightFit(), [PLACES.HKG.x, PLACES.HKG.y]), ...LAND);
  assert.equal(dots[0].attrs.cx, q.x.toFixed(2)); assert.equal(dots[0].attrs.cy, q.y.toFixed(2));
  assert.equal(dots[0].attrs.r, PLACE.DOT_R.toFixed(2), "landed: full size");
  assert.equal(names[0].textContent, "Hong Kong");
  assert.equal(dots[0].attrs.style, placeDotStyle()); assert.equal(names[0].attrs.style, placeLabelStyle());
  const a = Math.min(1, lightAlpha(t, sp.at, sp.dur, 1) / LIGHT.MAX);
  assert.equal(dots[0].attrs.opacity, a.toFixed(3)); assert.equal(names[0].attrs.opacity, a.toFixed(3));
});

test("before its word and after its window a place light paints nothing; it pops up from POP_FROM on the badge spring", () => {
  for (const t of [5.0, 5.9 - 1e-6, 5.9 + 10.0 + 1e-6]) {
    const rec = recorder(); paintLight(ctx(lightSp(), t, rec));
    assert.deepEqual(rec.all(), [], String(t));
  }
  const rec = recorder(); paintLight(ctx(lightSp(), 5.9 + 0.02, rec));
  const r = +rec.all().find((n) => n.cls === "vmplace").attrs.r;
  assert.ok(r >= PLACE.DOT_R * PLACE.POP_FROM - 1e-6 && r < PLACE.DOT_R, "springing up, never popping out of nothing");
});

test("ping: T46d's one pulse leaves the point, under the dot; absent, nothing", () => {
  const sp = lightSp({ ping: true }), t = pingAt(sp) + PING.EXPAND_S / 2, rec = recorder();
  paintLight(ctx(sp, t, rec));
  const rings = rec.out.filter((n) => n.cls === "vmping"), dotIdx = rec.out.findIndex((n) => n.cls === "vmplace");
  assert.equal(rings.length, 1);
  const q = vmScreen(null, idleXf("breath", t, 0), mapPoint(tightFit(), [PLACES.HKG.x, PLACES.HKG.y]), ...LAND);
  assert.equal(rings[0].attrs.cx, q.x.toFixed(2)); assert.equal(rings[0].attrs.cy, q.y.toFixed(2));
  assert.equal(rings[0].attrs.r, pingPose(sp, t).r.toFixed(2));
  assert.ok(rec.out.indexOf(rings[0]) < dotIdx, "the pulse is under the dot");
  const none = recorder(); paintLight(ctx(lightSp(), t, none));
  assert.deepEqual(none.all().filter((n) => n.cls === "vmping"), []);
});

test("the name sits right of the dot; where the frame cuts it, BELOW, then left, then above; it stays on the stage", () => {
  const off = PLACE.DOT_R + PLACE.GAP;
  assert.deepEqual([...PLACE_SIDES], ["right", "below", "left", "above"]);
  const right = placeLabelAt({ x: 900, y: 500 }, "Hong Kong", ...LAND);
  assert.equal(right.side, "right"); assert.equal(right.anchor, "start"); assert.equal(right.x, 900 + off);
  const below = placeLabelAt({ x: 1880, y: 500 }, "Hong Kong", ...LAND);   /* Hong Kong at the frame's right edge (read 2026-09-26) */
  assert.equal(below.side, "below"); assert.equal(below.anchor, "middle");
  assert.ok(below.y > 500 + off && below.x + 9 * PLACE.LABEL_PX * STAMP.CHAR_W / 2 <= LAND[0] - STAMP.EDGE, "under the dot, whole on the frame");
  const left = placeLabelAt({ x: 1880, y: 1070 }, "Hong Kong", ...LAND);
  assert.equal(left.side, "left"); assert.equal(left.anchor, "end"); assert.equal(left.x, 1880 - off);
  const top = placeLabelAt({ x: 900, y: 2 }, "Hong Kong", ...LAND);
  assert.ok(top.y >= STAMP.EDGE + PLACE.LABEL_PX, "never off the top");
  const foot = placeLabelAt({ x: 900, y: 1079 }, "Hong Kong", ...LAND);
  assert.ok(foot.y <= LAND[1] - STAMP.EDGE, "never off the foot");
});

test("the author's side wins (s106: the engine advises), and the painter reads it off the target", () => {
  for (const side of PLACE_SIDES) assert.equal(placeLabelAt({ x: 900, y: 500 }, "Hong Kong", ...LAND, PLACE.LABEL_PX, side).side, side);
  assert.equal(placeLabelAt({ x: 900, y: 500 }, "Hong Kong", ...LAND, PLACE.LABEL_PX, "sideways").side, "right", "an unknown side is the auto order");
  const rec = recorder();
  paintLight(ctx(lightSp({ target: hk({ side: "above" }) }), 7.0, rec));
  const name = rec.all().find((n) => n.cls === "vmplabel"), dot = rec.all().find((n) => n.cls === "vmplace");
  assert.equal(name.attrs["text-anchor"], "middle"); assert.ok(+name.attrs.y < +dot.attrs.cy, "above the dot");
});

test("the camera moves the dot with its place and never magnifies it (the stamp's rule)", () => {
  const cam = { s: 2, ox: 960, oy: 540, ax: 960, ay: 540 }, sp = lightSp(), t = sp.at + 1.0, rec = recorder();
  paintLight(ctx(sp, t, rec, cam));
  const dot = rec.all().find((n) => n.cls === "vmplace");
  const q = vmScreen(cam, idleXf("breath", t, 0), mapPoint(tightFit(), [PLACES.HKG.x, PLACES.HKG.y]), ...LAND);
  assert.equal(dot.attrs.cx, q.x.toFixed(2)); assert.equal(dot.attrs.r, PLACE.DOT_R.toFixed(2));
});

test("an arc runs to and from a place exactly as to a mappoint at the same point", () => {
  const usa = { kind: "country", id: "USA" }, mp = { kind: "mappoint", x: PLACES.HKG.x, y: PLACES.HKG.y };
  const paths = (to) => { const rec = recorder(); paintArc(ctx({ kind: "arc", at: 5.0, dur: 12.0, from: usa, to }, 7.0, rec)); return JSON.stringify(rec.out); };
  assert.equal(paths(hk()), paths(mp));
  const a = arcPath(tightFit(), DATA.countries.USA.centroid, [PLACES.HKG.x, PLACES.HKG.y], undefined,
                    arcBowSign(DATA.box, DATA.countries.USA.centroid, [PLACES.HKG.x, PLACES.HKG.y]));
  assert.ok(near(a.p1.x, mapPoint(tightFit(), [PLACES.HKG.x, PLACES.HKG.y]).x), "the head lands ON the point");
});

test("a stamp writes at a place as at a mappoint", () => {
  const paint = (target) => { const rec = recorder(); paintStamp(ctx({ kind: "stamp", at: 6.0, dur: 5.0, text: "customs", target }, 7.0, rec)); return JSON.stringify(rec.out); };
  assert.equal(paint(hk()), paint({ kind: "mappoint", x: PLACES.HKG.x, y: PLACES.HKG.y }));
});

test("a country's light paints what it painted before (no dot, no name)", () => {
  const rec = recorder();
  paintLight(ctx({ kind: "light", at: 5.0, dur: 10.0, target: { kind: "country", id: "CHN" } }, 6.0, rec));
  assert.ok(rec.all().some((n) => n.cls === "vmlit"));
  assert.deepEqual(rec.all().filter((n) => n.cls === "vmplace" || n.cls === "vmplabel"), []);
});
