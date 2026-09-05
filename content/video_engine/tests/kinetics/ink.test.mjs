// P43 T3 - Kubelka-Munk ink (44 s44.1). The failing case first: alpha's double pass vs K-M's, then the model's own
// identities (layers compose, hiding, the paper), the subtractive mix of two different inks, and the filter table.
import { test } from "node:test";
import assert from "node:assert/strict";
import { INK, hexToLin, linToHex, kmChannel, kmLayer, kmStack, alphaOver, chroma, kmHex, kmTable, kmFilterMarkup, ksFromR } from "../../scripts/kinetics/ink.mjs";

const CREAM = "#F4E6C7", INKS = { charcoal: "#25313C", coral: "#ED6A4A", teal: "#2E9E5B", sunflower: "#F5B72E", blood: "#B0201F" };
const cream = hexToLin(CREAM);
const lum = (c) => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
// the alpha an opaque film would need to match ONE K-M pass, per channel - then a second film at that alpha
const alphaDouble = (Rg, ink, single) => [0, 1, 2].map((i) => { const a = (Rg[i] - single[i]) / (Rg[i] - ink[i]); return Rg[i] * (1 - a) ** 2 + ink[i] * (1 - (1 - a) ** 2); });

test("44.1 ink over ink is darker by K-M than by alpha, calibrated so one pass agrees (every ink, every thickness)", () => {
  for (const hex of Object.values(INKS)) for (const X of [0.05, 0.1, 0.3, 0.6, 1.0]) {
    const ink = hexToLin(hex), single = kmLayer(cream, ink, X), km2 = kmLayer(cream, ink, 2 * X), al2 = alphaDouble(cream, ink, single);
    for (let i = 0; i < 3; i++) assert.ok(km2[i] <= al2[i] + 1e-12, `${hex} X=${X} ch${i}: km ${km2[i]} vs alpha ${al2[i]}`);
  }
});

test("44.1 layers of one ink compose: X1 over X2 IS a layer of X1 + X2 (so coverage can be summed and converted once)", () => {
  for (const hex of Object.values(INKS)) for (const [x1, x2] of [[0.05, 0.05], [0.1, 0.3], [0.02, 0.6]]) {
    const ink = hexToLin(hex), stacked = kmStack(cream, [{ ink, X: x2 }, { ink, X: x1 }]), one = kmLayer(cream, ink, x1 + x2);
    for (let i = 0; i < 3; i++) assert.ok(Math.abs(stacked[i] - one[i]) < 1e-9, `${hex} ${x1}+${x2} ch${i}`);
  }
});

test("ink over bare paper is the single stroke; zero thickness is the paper; infinite thickness hides the paper (R_inf)", () => {
  const ink = hexToLin(INKS.charcoal);
  assert.deepEqual(kmStack(cream, [{ ink, X: 0.2 }]), kmLayer(cream, ink, 0.2));
  assert.deepEqual(kmLayer(cream, ink, 0), cream);
  for (const hex of Object.values(INKS)) {
    const R = hexToLin(hex), deep = kmLayer(cream, R, 100);
    for (let i = 0; i < 3; i++) assert.ok(Math.abs(deep[i] - R[i]) < 1e-6, `${hex} ch${i} hides to its own colour`);
    assert.equal(kmHex("#16181c", hex, 100).toUpperCase(), hex.toUpperCase());
  }
});

test("K = 0 is a non-absorbing ink: it never darkens the paper, and with no thickness it is the paper", () => {
  assert.equal(ksFromR(1), ksFromR(0.995));   // the inversion is clamped away from the singularity
  for (const X of [0, 0.1, 1, 10]) { const R = kmChannel(0.7, 1.0, X); assert.ok(R >= 0.7 - 1e-12 && R <= 1, `X=${X}: ${R}`); }
  assert.equal(kmChannel(0.7, 1.0, 0), 0.7);
});

test("two DIFFERENT inks mix subtractively: sunflower over charcoal goes olive and darker where alpha goes tan", () => {
  const top = hexToLin(INKS.sunflower), ground = hexToLin(INKS.charcoal);
  for (const X of [0.15, 0.4, 1.0]) {
    const km = kmLayer(ground, top, X);
    const single = kmLayer(cream, top, X), a = [0, 1, 2].reduce((s, i) => s + (cream[i] - single[i]) / (cream[i] - top[i]), 0) / 3;
    const al = alphaOver(ground, top, a);
    assert.ok(al[0] - al[1] > 0.1, `alpha is tan: R ${al[0]} well above G ${al[1]}`);
    assert.ok(km[0] - km[1] < (al[0] - al[1]) * 0.5, `K-M is olive: its R-G gap ${km[0] - km[1]} is under half the film's ${al[0] - al[1]}`);
    if (X < 1) assert.ok(lum(km) < lum(al), "a thin K-M layer is darker than the film (at full hiding both are the yellow)");
  }
  const km = kmLayer(hexToLin(INKS.teal), hexToLin(INKS.coral), 0.4), al = alphaOver(hexToLin(INKS.teal), hexToLin(INKS.coral), 0.5);
  assert.ok(lum(km) < lum(al) && chroma(km) < chroma(al), "coral over teal: K-M darker and browner, alpha brighter and pinker");
});

test("the filter table runs from the paper to exactly the ink at one full stain, monotone, and its markup carries it", () => {
  const t = kmTable(CREAM, INKS.charcoal);
  assert.equal(t.n, INK.TABLE_N);
  assert.ok(Math.abs(t.r[0] - 0xF4 / 255) < 1e-9 && Math.abs(t.b[0] - 0xC7 / 255) < 1e-9, "starts on the cream");
  const full = Math.ceil(INK.COVERAGE * (t.n - 1));
  for (const [col, v] of [[t.r, 0x25], [t.g, 0x31], [t.b, 0x3C]]) {
    for (let i = full; i < t.n; i++) assert.equal(col[i], v / 255, "one full stain IS the ink");
    for (let i = 1; i < t.n; i++) assert.ok(col[i] <= col[i - 1] + 1e-12, "never lightens as ink accumulates");
  }
  const m = kmFilterMarkup(CREAM, INKS.charcoal);
  assert.equal((m.match(/tableValues=/g) || []).length, 3);
  assert.ok(m.includes('slope="' + INK.ALPHA_SLOPE + '"') && m.startsWith("<feColorMatrix"));
  assert.equal(linToHex(hexToLin("#25313C")), "#25313c");
});
