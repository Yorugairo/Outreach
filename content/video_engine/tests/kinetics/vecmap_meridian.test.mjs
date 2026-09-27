// P73 T6 (R26-406) - A PACIFIC-CENTRED MAP. The compiler ships a vector map re-centred on `;meridian=<deg>` under its own
// key (`map:world-110m@150`: every ring moved by build_world_map.recentre_x, cut at the new seam, joined at the old one,
// centroids and boxes moved with them, and the document's own `meridian`). The player's one new line is vmRecentreX -
// the SAME formula, in JS - for the points the asset does not carry: a place's x (the gazetteer's, in the file's units)
// and a typed mappoint's. These tests pin that the file (no `meridian`) is the identity to the bit, that the two formulas
// agree, that the United States -> Hong Kong arc crosses the Pacific on the re-centred map (and Greenwich on the file),
// and that `;fit=tight` still frames the focus set under a new meridian.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { mapData, mapFit, mapInvert, vmTarget, vmRecentreX, worldFit, arcPath, arcBowSign } from "../../scripts/species/vecmap.mjs";

const read = (rel) => readFileSync(fileURLToPath(new URL(rel, import.meta.url)), "utf-8");
const RAW = read("../../assets/maps/world-110m.paths.json");
const PLACES = JSON.parse(read("../../assets/maps/places.json")).places;
const PACIFIC_URIS = JSON.parse(read("../golden/sources/vecmap-pacific.uris.json"));
const RAW150 = PACIFIC_URIS["map:world-110m@150"];
const DATA = mapData(RAW), DATA150 = mapData(RAW150);
const LAND = [1920, 1080], PORT = [1080, 1920];
const near = (a, b, eps) => Math.abs(a - b) <= eps;
const place = (id) => ({ kind: "place", id, x: PLACES[id].x, y: PLACES[id].y, label: PLACES[id].label });
const lonOf = (x) => x / 1000 * 360 - 180;

test("the file carries no meridian, and on it the formula is the identity to the bit", () => {
  assert.equal(DATA.meridian, undefined);
  for (const x of [0, 0.001, 123.456, 500, 817.175, 999.999, 1000]) assert.equal(vmRecentreX(DATA, x), x);
  assert.equal(vmRecentreX(null, 12.5), 12.5);
  assert.deepEqual(vmTarget(DATA, place("HKG")), [PLACES.HKG.x, PLACES.HKG.y]);
  assert.deepEqual(vmTarget(DATA, { kind: "mappoint", x: 640, y: 165 }), [640, 165]);
});

test("the Pacific asset is the compiler's re-centred world", () => {
  assert.ok(RAW150, "the golden's uris carry map:world-110m@150");
  assert.equal(DATA150.meridian, 150);
  assert.deepEqual(DATA150.box, DATA.box);
  assert.deepEqual(Object.keys(DATA150.countries).sort(), Object.keys(DATA.countries).sort());
});

test("the JS formula is the Python one: 150 E in the middle, Hong Kong 35.8 deg west of it", () => {
  assert.ok(near(vmRecentreX(DATA150, 916.667), 500, 1e-3));
  assert.ok(near(vmRecentreX(DATA150, PLACES.HKG.x), 400.508, 1e-3));   // test_pacific_map pins the same number
  for (const id of Object.keys(PLACES)) {
    const want = ((PLACES[id].lon - 150 + 180) % 360 + 360) % 360 / 360 * 1000;
    assert.ok(near(vmRecentreX(DATA150, PLACES[id].x), want, 1.5e-3), id);
  }
  // every country's centroid in the asset (Python moved it) is the file's centroid through the JS line
  for (const [id, c] of Object.entries(DATA150.countries)) {
    assert.ok(near(c.centroid[0], vmRecentreX(DATA150, DATA.countries[id].centroid[0]), 1e-3), id);
    assert.equal(c.centroid[1], DATA.countries[id].centroid[1], id);
  }
  // the wrap: a point never leaves the box
  for (const x of [0, 83.333, 83.334, 583.333, 999.999]) {
    const v = vmRecentreX(DATA150, x);
    assert.ok(v >= 0 && v < 1000, String(x));
  }
});

test("a place and a mappoint are moved by the player; a country's centroid comes moved in the asset", () => {
  const [hx, hy] = vmTarget(DATA150, place("HKG"));
  assert.ok(near(hx, 400.508, 1e-3)); assert.equal(hy, PLACES.HKG.y);
  const [mx] = vmTarget(DATA150, { kind: "mappoint", x: 916.667, y: 250 });
  assert.ok(near(mx, 500, 1e-3));
  assert.deepEqual(vmTarget(DATA150, { kind: "country", id: "USA" }), DATA150.countries.USA.centroid);
});

const routeXs = (data, fit) => {
  const from = vmTarget(data, { kind: "country", id: "USA" }), to = vmTarget(data, place("HKG"));
  const arc = arcPath(fit, from, to, undefined, arcBowSign(data.box, from, to));
  return { from, to, xs: arc.pts.map((q) => mapInvert(fit, q)[0]) };
};

test("the United States -> Hong Kong arc crosses the PACIFIC on the re-centred map, and Greenwich on the file", () => {
  const fit150 = worldFit(DATA150, { focus: ["USA", "CHN"], fit: "tight" }, ...LAND);
  const p = routeXs(DATA150, fit150);
  const lo = Math.min(...p.xs), hi = Math.max(...p.xs), oldSeam = vmRecentreX(DATA150, 0), greenwich = vmRecentreX(DATA150, 500);
  assert.ok(lo <= oldSeam && oldSeam <= hi, "it crosses 180 (the date line) - the Pacific");
  assert.ok(!(lo <= greenwich && greenwich <= hi), "and never Greenwich");
  assert.ok(hi - lo < 500, "the short way: less than half the world");
  const fit0 = worldFit(DATA, { focus: ["USA", "CHN"], fit: "tight" }, ...LAND);
  const g = routeXs(DATA, fit0);
  assert.ok(Math.min(...g.xs) <= 500 && 500 <= Math.max(...g.xs), "on the file the same arc crosses Greenwich (R26-406)");
  assert.ok(lonOf(Math.max(...g.xs)) - lonOf(Math.min(...g.xs)) > 180, "... the long way round");
});

test(";fit=tight still frames the focus set under a new meridian, tighter than the Greenwich box", () => {
  for (const [W, H] of [LAND, PORT]) {
    const world = { focus: ["USA", "CHN"], fit: "tight" };
    const f150 = worldFit(DATA150, world, W, H), f0 = worldFit(DATA, world, W, H);
    for (const id of world.focus) {
      const [x0, y0, x1, y1] = DATA150.countries[id].bbox;
      for (const [x, y] of [[x0, y0], [x1, y1]]) {
        const sx = f150.sx * x + f150.tx, sy = f150.sy * y + f150.ty;
        assert.ok(sx >= 0 && sx <= W && sy >= 0 && sy <= H, `${id} at ${W}x${H}`);
      }
    }
    assert.ok(f150.sx > f0.sx, `the Pacific box is narrower, so the fit is closer (${W}x${H})`);
    assert.deepEqual(f150, mapFit(DATA150.box, world.focus.map((id) => DATA150.countries[id].bbox), W, H, undefined, { tight: true }));
  }
});
