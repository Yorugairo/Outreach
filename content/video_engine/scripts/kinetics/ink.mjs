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

export const INK = Object.freeze({ S1: 0.03, TABLE_N: 33, ALPHA_SLOPE: 8, COVERAGE: 0.5, HIGHLIGHT_X: 0.4, WASH_NEUTRAL: 0.8 });
/* S1: a full stain is thin - carbon hides fast (44), and 0.03 keeps the first wash LIGHT (operator: 'start out more as a lighter gray');
   HIGHLIGHT_X: the band as a layer; WASH_NEUTRAL: how far a THIN layer's per-channel K/S is pulled to their mean - a thin charcoal
   layer is bluish by the model (its blue channel absorbs least), the operator wants grey, and the blend relaxes to the exact
   ink at full coverage so the flood still ends on #25313C (operator, 2026-09-05: 'less blue tinge') */

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
export const srgbToLin = (c) => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
export const linToSrgb = (v) => { v = clamp(v, 0, 1); return v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055; };
export const hexToLin = (hex) => { const h = hex.replace("#", ""); return [0, 2, 4].map((i) => srgbToLin(parseInt(h.slice(i, i + 2), 16) / 255)); };
export const linToHex = (rgb) => "#" + rgb.map((v) => Math.round(linToSrgb(v) * 255).toString(16).padStart(2, "0")).join("");

/* K/S of a pigment from its full-coverage (infinite-thickness) reflectance - the K-M inversion, one channel. */
export const ksFromR = (Rinf) => { const R = clamp(Rinf, 0.005, 0.995); return (1 - R) * (1 - R) / (2 * R); };

/* One channel from its K/S: a layer of optical thickness SX over a ground Rg. */
export const kmChannelKS = (Rg, ks, SX) => {
  if (!(SX > 0)) return Rg;
  const a = 1 + ks, b = Math.sqrt(a * a - 1);
  if (b === 0) return Rg;                                       /* K = 0: a non-absorbing ink - see the tests */
  const x = b * SX, coth = x > 20 ? 1 : 1 / Math.tanh(x);
  return (1 - Rg * (a - b * coth)) / (a - Rg + b * coth);
};
/* One channel of an ink with full-coverage reflectance Rinf. */
export const kmChannel = (Rg, Rinf, SX) => kmChannelKS(Rg, ksFromR(Rinf), SX);

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
    const c = i / (n - 1), full = c >= P.COVERAGE - 1e-9, f = Math.min(1, c / P.COVERAGE);
    const ks = ink.map(ksFromR), mean = (ks[0] + ks[1] + ks[2]) / 3, w = (P.WASH_NEUTRAL || 0) * (1 - f * f * f * f);   /* neutral while thin and mid, the ink's own at full */
    const R = full ? ink : [0, 1, 2].map((k) => kmChannelKS(paper[k], ks[k] * (1 - w) + mean * w, f * P.S1));
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

/* THE ERRATIC SOAK (operator, 2026-09-05: "more erratic ... the variance spread throughout, almost like a mesh with some
   spots having higher attraction than others"; 44 s44.3 - wicking through a random permeability field). The paper carries
   a fixed ATTRACTION field (feTurbulence type "turbulence": the |noise| sum is a mesh of ridges between bright spots).
   Each stain is SOFT coverage (a radial gradient, soakGradientMarkup) that grows outward; the filter multiplies the summed
   coverage by (BASE + GAIN * attraction) and the K-M stage's alpha ramp then decides where ink has arrived - a high-attraction
   spot lights up ahead of the front, the front travels along the ridges, low spots stay dry inside a stain until the
   coverage is heavy, and the K-M table deepens everything that overlaps. WOBBLE is the macro displacement the soak already
   had; BLUR wets the result. All dials (42 s42.5). */
/* round 3 (operator, 2026-09-05: "more wobble ... a higher grain"): WOBBLE_SCALE up and its field a little busier; GRAIN is a second,
   fine attraction field multiplied in after the mesh - the speckle inside and along the front */
/* MESH (operator, 2026-09-05, after seeing it in motion: "it absolutely looks like a burn-in because of the boil ... tempted to just
   revert to the original kubelka munk, i also don't like how the spiral looks now when it soaks back up the layer"): OFF by default -
   the K-M soak is the original chain (the soak's own wobble and blur, flat white stains, the table) and the retract drags clean
   stains down the drain. The attraction field, the grain and the motion below only exist behind MESH: true. */
/* PLAIN_* (operator: "more wobble without causing the issues"): a deeper, busier outline displacement than the alpha soak's 110,
   and a slow CREEP of that low-frequency noise through the soak (PLAIN_DRIFT px per unit soak, PLAIN_BREATH on the scale) -
   smooth and slow reads as ink moving; the fast fine grain that read as a burn-in is not part of it */
export const SOAK = Object.freeze({ MESH: false, PLAIN_FREQ: "0.007 0.011", PLAIN_SCALE: 170, PLAIN_BLUR: 12, PLAIN_DRIFT: 90, PLAIN_BREATH: 0.15,
                                    WOBBLE_FREQ: "0.008 0.012", WOBBLE_OCT: 3, WOBBLE_SCALE: 180, ATTR_FREQ: "0.008 0.011", ATTR_OCT: 4,
                                    ATTR_BASE: 0.25, ATTR_GAIN: 1.8, GRAIN_FREQ: "0.055 0.07", GRAIN_OCT: 2, GRAIN_BASE: 0.65, GRAIN_GAIN: 0.7,
                                    BLUR: 5, GRAD_MID: 0.55, GRAD_MID_A: 0.85,
                                    /* the MOTION (operator: 'wriggling / morphing / creeping / crawling'): drifts in field px per unit soak, the breath
                                       as a share of WOBBLE_SCALE; every drift stays inside the filter's 25% margin (1690 * 0.25 = 422 px at fk 1) */
                                    WOBBLE_DRIFT: 150, WOBBLE_BREATH: 0.3, WOBBLE_CYCLES: 2.5, ATTR_DRIFT: 60, GRAIN_DRIFT: 260 });

export const soakGradientMarkup = (id, o = {}) => {
  const P = Object.assign({}, SOAK, o);
  return '<radialGradient id="' + id + '"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="' + P.GRAD_MID + '" stop-color="#fff" stop-opacity="' + P.GRAD_MID_A + '"/>'
    + '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>';
};

export const soakFilterMarkup = (seed, fk, paperHex, inkHex, o = {}) => {
  const P = Object.assign({}, INK, SOAK, o), s = seed & 255;
  if (!P.MESH) return '<feTurbulence type="fractalNoise" baseFrequency="' + P.PLAIN_FREQ + '" numOctaves="3" seed="' + s + '" result="n0"/>'
    + '<feOffset in="n0" dx="0" dy="0" result="n" id="lpsoakw' + s + '"/>'
    + '<feDisplacementMap in="SourceGraphic" in2="n" scale="' + Math.round(P.PLAIN_SCALE * fk) + '" xChannelSelector="R" yChannelSelector="G" id="lpsoakd' + s + '"/>'
    + '<feGaussianBlur stdDeviation="' + P.PLAIN_BLUR + '"/>' + kmFilterMarkup(paperHex, inkHex, P);
  return '<feTurbulence type="fractalNoise" baseFrequency="' + P.WOBBLE_FREQ + '" numOctaves="' + P.WOBBLE_OCT + '" seed="' + s + '" result="n0"/>'
    + '<feOffset in="n0" dx="0" dy="0" result="n" id="lpsoakw' + s + '"/>'
    + '<feDisplacementMap in="SourceGraphic" in2="n" scale="' + Math.round(P.WOBBLE_SCALE * fk) + '" xChannelSelector="R" yChannelSelector="G" result="d" id="lpsoakd' + s + '"/>'
    + '<feTurbulence type="turbulence" baseFrequency="' + P.ATTR_FREQ + '" numOctaves="' + P.ATTR_OCT + '" seed="' + ((s + 13) & 255) + '" result="att0"/>'
    + '<feOffset in="att0" dx="0" dy="0" result="att" id="lpsoaka' + s + '"/>'
    + '<feComposite in="d" in2="att" operator="arithmetic" k1="' + P.ATTR_GAIN + '" k2="' + P.ATTR_BASE + '" k3="0" k4="0" result="c"/>'
    + '<feTurbulence type="fractalNoise" baseFrequency="' + P.GRAIN_FREQ + '" numOctaves="' + P.GRAIN_OCT + '" seed="' + ((s + 29) & 255) + '" result="grain0"/>'
    + '<feOffset in="grain0" dx="0" dy="0" result="grain" id="lpsoakg' + s + '"/>'
    + '<feComposite in="c" in2="grain" operator="arithmetic" k1="' + P.GRAIN_GAIN + '" k2="' + P.GRAIN_BASE + '" k3="0" k4="0" result="cg"/>'
    + '<feGaussianBlur in="cg" stdDeviation="' + P.BLUR + '"/>'
    + kmFilterMarkup(paperHex, inkHex, P);
};

/* the fields' motion at soak progress u in [0, 1] - a pure function, so a scrubbed frame is the played one: the wobble noise
   slides and its displacement breathes (the outline wriggles and morphs), the attraction mesh creeps (the dark spots migrate
   and the front crawls after them), the grain boils. Offsets in field px (fk scales a portrait field). */
export const soakAnim = (u, fk = 1, o = {}) => {
  const P = Object.assign({}, SOAK, o), tp = Math.PI * 2, k = Math.min(1, Math.max(0, u));
  if (!P.MESH) return {   /* the plain chain: only the outline noise creeps, slowly, and its depth breathes a little */
    wob: [P.PLAIN_DRIFT * fk * k, P.PLAIN_DRIFT * fk * 0.5 * Math.sin(k * tp * 0.75)], att: [0, 0], grain: [0, 0],
    scale: P.PLAIN_SCALE * fk * (1 + P.PLAIN_BREATH * Math.sin(k * tp * 2)),
  };
  return {
    wob: [P.WOBBLE_DRIFT * fk * k, P.WOBBLE_DRIFT * fk * 0.6 * Math.sin(k * tp * 0.75)],
    att: [P.ATTR_DRIFT * fk * Math.sin(k * tp * 0.5), -(P.ATTR_DRIFT * fk * k) || 0],
    grain: [P.GRAIN_DRIFT * fk * k, P.GRAIN_DRIFT * fk * 0.5 * Math.sin(k * tp)],
    scale: P.WOBBLE_SCALE * fk * (1 + P.WOBBLE_BREATH * Math.sin(k * tp * P.WOBBLE_CYCLES)),
  };
};
export const soakAnimIds = (seed) => { const s = seed & 255; return { wob: "lpsoakw" + s, att: "lpsoaka" + s, grain: "lpsoakg" + s, disp: "lpsoakd" + s }; };
