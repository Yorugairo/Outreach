// P50 T9 - N-TIER PAGES (R26-24; Bravos shots 35-36). The module is math only - the page's builder
// owns the DOM - so these tests pin the bands (and their agreement with the python mirror the
// compiler docks against), the honest zero, the band's own scale and the in-turn build clock.
import { test } from "node:test";
import assert from "node:assert/strict";
import { TIERS, tierBands, tierDomain, tierY, tierTicks, tierStagger, tierBuildK } from "../../scripts/species/tiers.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the dials are the tiers page's, and a gutter never eats a band", () => {
  assert.ok(TIERS.GAP > 0 && TIERS.GAP < 0.5, "a gutter that is half a band is a second page");
  assert.ok(TIERS.PAD > 0 && TIERS.PAD < 0.5);
  assert.ok(TIERS.TICKS >= 2 && TIERS.STAGGER > 0 && TIERS.STAGGER < 1);
});

// ------------------------------------------------------------------ the bands
test("N bands fill the plot top to bottom, equal, with one gutter between each pair", () => {
  const bands = tierBands(100, 500, 3);
  assert.equal(bands.length, 3);
  assert.ok(near(bands[0].y0, 100), "the first band starts at the plot's top");
  assert.ok(near(bands[2].y1, 500), "the last one ends at its foot");
  for (const b of bands) assert.ok(near(b.h, bands[0].h), "equal bands: a small multiple compares shape, and an unequal band lies about it");
  assert.ok(near(bands[1].y0 - bands[0].y1, bands[0].h * TIERS.GAP), "the gutter is GAP of a band's height");
  assert.deepEqual(tierBands(0, 100, 0), []);
  assert.equal(tierBands(0, 100, 1).length, 1);
  assert.ok(near(tierBands(0, 100, 1)[0].h, 100), "one band is the whole plot (the compiler refuses a one-tier page; the law still holds)");
});

test("the bands are the SAME bands ledger_page.tier_bands reports to the compiler (one law, two languages)", () => {
  // ledger_page.tier_bands on a 16:9 plot {y: 270, h: 556}: [{y 270, h 253}, {y 573, h 253}]
  const bands = tierBands(270, 270 + 556, 2);
  assert.equal(Math.round(bands[0].y0), 270);
  assert.equal(Math.round(bands[0].h), 253);
  assert.equal(Math.round(bands[1].y0), 573);
  assert.equal(Math.round(bands[1].h), 253);
  // ... and on a 9:16 plot {y: 464, h: 724}: [{y 464, h 329}, {y 859, h 329}]
  const port = tierBands(464, 464 + 724, 2);
  assert.equal(Math.round(port[0].h), 329);
  assert.equal(Math.round(port[1].y0), 859);
});

// ------------------------------------------------------------- the honest zero
test("a band's domain keeps its ZERO by default, and says so when it is dropped (E53 s4)", () => {
  const [lo, hi] = tierDomain([320, 300, 292]);
  assert.equal(lo, 0, "an honest zero: a band read shape-against-shape may not drop its floor quietly");
  assert.ok(hi > 320);
  const [lo2, hi2] = tierDomain([320, 300, 292], false);
  assert.ok(lo2 > 0 && lo2 < 292 && hi2 > 320, "the opt-out pads both ends instead");
  const [lo3, hi3] = tierDomain([-40, 12]);
  assert.ok(lo3 <= -40 && hi3 >= 12, "a signed band keeps both ends and the zero between them");
  assert.deepEqual(tierDomain([]), [0, 1]);
  assert.deepEqual(tierDomain(["x", null]), [0, 1], "a band of nothing is not a scale");
});

test("a value's y is inside its own band, the floor at the band's foot", () => {
  const band = tierBands(100, 500, 2)[1];
  const [lo, hi] = tierDomain([0, 100]);
  assert.ok(near(tierY(band, lo, hi, 0), band.y1), "zero sits on the band's floor");
  assert.ok(tierY(band, lo, hi, 100) > band.y0, "the tallest value keeps PAD of headroom");
  assert.ok(tierY(band, lo, hi, 100) < tierY(band, lo, hi, 50), "up is up");
  assert.ok(Number.isFinite(tierY(band, 0, 0, 5)), "a domain of zero width does not divide by zero");
});

test("a band's gridlines are nice numbers and include the zero when the domain holds it", () => {
  const ticks = tierTicks(0, 340);
  assert.ok(ticks.length >= 2 && ticks.length <= 5, ticks.join(","));
  assert.ok(ticks.includes(0), "an honest zero that is not drawn is not read");
  assert.ok(ticks.every((v) => v >= 0 && v <= 340 + 1e-9));
  assert.ok(tierTicks(-40, 40).includes(0));
});

// -------------------------------------------------------------- the build clock
test("the bands draw IN TURN: band i starts later than band i-1, and every band lands by the end", () => {
  const n = 3;
  assert.equal(tierStagger(0, n), 0, "the first band starts with the page");
  assert.ok(tierStagger(1, n) > 0 && tierStagger(2, n) > tierStagger(1, n));
  assert.equal(tierStagger(0, 1), 0, "one band has nothing to wait for");
  for (let i = 0; i < n; i++) {
    assert.equal(tierBuildK(0, i, n), 0);
    assert.equal(tierBuildK(1, i, n), 1, "no band is still drawing when the build clock ends");
    assert.ok(tierBuildK(0.5, 0, n) >= tierBuildK(0.5, 1, n), "the first band is always ahead of the second");
  }
  assert.ok(tierBuildK(tierStagger(2, n) + 1e-6, 2, n) >= 0);
});
