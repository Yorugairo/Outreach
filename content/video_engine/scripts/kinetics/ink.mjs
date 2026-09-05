/* kinetics/ink.mjs - Kubelka-Munk ink (44 s44.1; FINDING-the-animation-math s6; 47 s5b). SOURCE OF TRUTH, inlined into
   the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN ink and KINETICS:END (P43 T3). Behind
   kinetics.km_ink.
   The defect: alpha compositing (dst (1 - a) + src a) models an opaque film over a background. Layered translucent
   pigment obeys two-flux radiative transfer (Kubelka & Munk 1931): dI/dz = -(K + S) I + S J, -dJ/dz = -(K + S) J + S I,
   K absorption, S scattering. Two ink passes by alpha give a dull desaturated grey; by K-M they DEEPEN, and two
   different inks mix subtractively (a yellow over a blue-grey goes green, never grey).
   The model, per channel in LINEAR reflectance: an ink's full-coverage colour is its R_inf, so K/S = (1 - R_inf)^2 /
   (2 R_inf) (the K-M inversion); a layer of optical thickness SX over a ground Rg reflects
       R = (1 - Rg (a - b coth(b S X))) / (a - Rg + b coth(b S X)),  a = 1 + K/S,  b = sqrt(a^2 - 1).
   Layers of one ink compose: a layer of X1 over a layer of X2 IS a layer of X1 + X2 - which is why coverage can be
   summed in a buffer and converted once (kmFilterMarkup: the stains add their coverage with plus-lighter, the filter
   moves that coverage into the colour channels and a per-channel table maps it through this curve).
   The dials - S1 (the optical thickness of one full stain), the table resolution, the alpha slope, the coverage
   that means one full stain - are ours to tune (42 s42.5 / 44); the two-flux model is the finding. */

export const INK = Object.freeze({ S1: 0.05, TABLE_N: 33, ALPHA_SLOPE: 8, COVERAGE: 0.5, HIGHLIGHT_X: 0.4 });   /* S1: a full stain is thin - carbon hides fast (44); HIGHLIGHT_X: the band as a layer */

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
export const srgbToLin = (c) => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
export const linToSrgb = (v) => { v = clamp(v, 0, 1); return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055; };
export const hexToLin = (hex) => { const h = hex.replace("#", ""); return [0, 2, 4].map((i) => srgbToLin(parseInt(h.slice(i, i + 2), 16) / 255)); };
export const linToHex = (rgb) => "#" + rgb.map((v) => Math.round(linToSrgb(v) * 255).toString(16).padStart(2, "0")).join("");

/* K/S of a pigment from its full-coverage (infinite-thickness) reflectance - the K-M inversion, one channel. */
export const ksFromR = (Rinf) => { const R = clamp(Rinf, 0.005, 0.995); return (1 - R) * (1 - R) / (2 * R); };

/* One channel: a layer of optical thickness SX of an ink with full-coverage reflectance Rinf over a ground Rg. */
export const kmChannel = (Rg, Rinf, SX) => {
  if (!(SX > 0)) return Rg;
  const a = 1 + ksFromR(Rinf), b = Math.sqrt(a * a - 1);
  if (b === 0) return Rg;                                       /* K = 0: a non-absorbing ink - see the tests */
  const x = b * SX, coth = x > 20 ? 1 : 1 / Math.tanh(x);
  return (1 - Rg * (a - b * coth)) / (a - Rg + b * coth);
};

/* Three channels of linear reflectance. */
export const kmLayer = (Rg, Rinf, SX) => [0, 1, 2].map((i) => kmChannel(Rg[i], Rinf[i], SX));

/* Layers from the paper up: [{ ink: [r,g,b] linear, X }]. */
export const kmStack = (paper, layers) => layers.reduce((Rg, l) => kmLayer(Rg, l.ink, l.X), paper);

/* The wrong operator, kept as the else branch and the tests' reference: an opaque film at coverage a. */
export const alphaOver = (Rg, Rinf, a) => [0, 1, 2].map((i) => Rg[i] * (1 - a) + Rinf[i] * a);

export const chroma = (rgb) => Math.max(...rgb) - Math.min(...rgb);

/* The hex of one ink layer over a known ground - the highlighter band over the chart's dark ground is exactly this,
   a flat fill at opacity 1 instead of a translucent rect. */
export const kmHex = (groundHex, inkHex, SX) => linToHex(kmLayer(hexToLin(groundHex), hexToLin(inkHex), SX));

/* The coverage -> sRGB table for a filter: coverage c in [0, 1] (the summed stain alpha), c = COVERAGE is one full stain of
   thickness S1, so thickness = c / COVERAGE * S1; at and past a full stain the entry IS the ink (the field's final state is
   the charcoal by definition - hiding is complete, no residual from a finite S1). */
export const kmTable = (paperHex, inkHex, o = {}) => {
  const P = Object.assign({}, INK, o), paper = hexToLin(paperHex), ink = hexToLin(inkHex), n = P.TABLE_N;
  const cols = [[], [], []];
  for (let i = 0; i < n; i++) {
    const c = i / (n - 1), full = c >= P.COVERAGE - 1e-9;
    const R = full ? ink : kmLayer(paper, ink, c / P.COVERAGE * P.S1);
    for (let k = 0; k < 3; k++) cols[k].push(full ? srgbTo8(inkHex, k) : linToSrgb(R[k]));
  }
  return { r: cols[0], g: cols[1], b: cols[2], n };
};
const srgbTo8 = (hex, k) => parseInt(hex.replace("#", "").slice(k * 2, k * 2 + 2), 16) / 255;

/* SVG filter primitives that turn summed white coverage (the stains drawn white, mix-blend-mode: plus-lighter) into K-M
   ink: alpha into the colour channels, the table per channel, alpha steepened so a stain's body is opaque and its edge
   is the table's own gradient rather than a fade. Appended after the soak's displacement and blur. */
export const kmFilterMarkup = (paperHex, inkHex, o = {}) => {
  const P = Object.assign({}, INK, o), t = kmTable(paperHex, inkHex, P), f = (a) => a.map((v) => v.toFixed(4)).join(" ");
  return '<feColorMatrix type="matrix" values="0 0 0 1 0  0 0 0 1 0  0 0 0 1 0  0 0 0 1 0"/>'
    + '<feComponentTransfer><feFuncR type="table" tableValues="' + f(t.r) + '"/><feFuncG type="table" tableValues="' + f(t.g) + '"/>'
    + '<feFuncB type="table" tableValues="' + f(t.b) + '"/><feFuncA type="linear" slope="' + P.ALPHA_SLOPE + '" intercept="0"/></feComponentTransfer>';
};
