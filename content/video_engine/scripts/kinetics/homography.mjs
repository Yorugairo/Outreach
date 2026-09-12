/* kinetics/homography.mjs - THE PLANAR PROJECTION (P50 T7, the ART-embed world; Gemini's Bravos reading of their
   studio display, 2026-09-10 §4: "any planar element can be projected into perspective by a standard 3x3 planar
   homography H with h22 = 1"). SOURCE OF TRUTH, inlined into the scene-evidence engine by sync_kinetics.py between
   KINETICS:BEGIN homography and KINETICS:END. No imports: this is arithmetic, and it sits early in the region order.

   WHAT IT IS FOR. E33 says a generated plate has no addressable coordinate space - a diffusion model decided where
   the wall is, so nothing can be docked to it. The ART-embed grammar answers that by MEASURING one flat surface in
   the painting and declaring its four corners on the plate's manifest (`embed: {poster: {quad: [...]}}`); this module
   turns those four corners into the one transform that carries a card - its badges, its underline, its type - onto
   that surface. The surface itself is BLANK in the painting (E33 / doc 15 §4: no facts inside generated pixels); the
   information layer is composited, in perspective, here.

   THE MATH, all of it closed form and pure - no fitting, no iteration, so the same quad gives the same matrix on
   every machine and a seek to any t paints one frame:

     [x']   [h00 h01 h02] [x]
     [y'] = [h10 h11 h12] [y]      X = x'/w'   Y = y'/w'     (h22 = 1: the scale is fixed, 8 unknowns remain)
     [w']   [h20 h21   1] [1]

   The unit square (0,0) (1,0) (1,1) (0,1) -> the quad TL TR BR BL solves in closed form (Heckbert 1989,
   "Fundamentals of Texture Mapping and Image Warping", §2.2 - the projective mapping from the unit square):
     dx1 = x1-x2, dx2 = x3-x2, dx3 = x0-x1+x2-x3   (and the same in y)
     when dx3 = dy3 = 0 the quad is a parallelogram and the map is AFFINE (h20 = h21 = 0);
     otherwise h20, h21 come from one 2x2 solve and the rest follows by substitution.
   Everything else here is composition: `hMul` (normalised so h22 stays 1 - the law), `hTranslate`, `hAffine` (a CSS
   `matrix(a b c d e f)` lifted into the same 3x3), and `cssMatrix3d`, which writes H as the 4x4 CSS takes:
   column-major, the z row and column left identity, and the perspective terms in the fourth ROW of the written
   argument list (m14 = h20, m24 = h21) - that is what makes the browser divide by w' per pixel instead of shearing. */

/* a homography as the 8 free entries, row major: [h00, h01, h02, h10, h11, h12, h20, h21]; h22 is 1 by law. */
export const H_IDENTITY = Object.freeze([1, 0, 0, 0, 1, 0, 0, 0]);

const num = (v) => typeof v === "number" && Number.isFinite(v);

/* the four corners as [[x, y] x 4] in TL TR BR BL order, or null - the shape every entry point here takes */
export const quadPoints = (quad) => {
  if (!Array.isArray(quad) || quad.length !== 4) return null;
  const pts = quad.map((p) => (Array.isArray(p) && p.length >= 2 && num(+p[0]) && num(+p[1]) ? [+p[0], +p[1]] : null));
  return pts.every(Boolean) ? pts : null;
};

/* THE UNIT SQUARE -> THE QUAD. (0,0) -> TL, (1,0) -> TR, (1,1) -> BR, (0,1) -> BL. Null on a degenerate quad
   (three corners on one line), which is the one input with no projective map at all. */
export const hFromUnitSquare = (quad) => {
  const p = quadPoints(quad);
  if (!p) return null;
  const [[x0, y0], [x1, y1], [x2, y2], [x3, y3]] = p;
  const dx3 = x0 - x1 + x2 - x3, dy3 = y0 - y1 + y2 - y3;
  if (Math.abs(dx3) < 1e-12 && Math.abs(dy3) < 1e-12) {   /* a parallelogram: the map is affine, and exactly affine */
    return [x1 - x0, x2 - x1, x0, y1 - y0, y2 - y1, y0, 0, 0];
  }
  const dx1 = x1 - x2, dx2 = x3 - x2, dy1 = y1 - y2, dy2 = y3 - y2;
  const den = dx1 * dy2 - dx2 * dy1;
  if (Math.abs(den) < 1e-12) return null;
  const h20 = (dx3 * dy2 - dx2 * dy3) / den, h21 = (dx1 * dy3 - dx3 * dy1) / den;
  return [x1 - x0 + h20 * x1, x3 - x0 + h21 * x3, x0,
          y1 - y0 + h20 * y1, y3 - y0 + h21 * y3, y0, h20, h21];
};

/* the point (x, y) through H, or null when it lands on the horizon (w' = 0) */
export const hApply = (h, x, y) => {
  if (!h) return null;
  const w = h[6] * x + h[7] * y + 1;
  if (Math.abs(w) < 1e-12) return null;
  return [(h[0] * x + h[1] * y + h[2]) / w, (h[3] * x + h[4] * y + h[5]) / w];
};

/* A then B: the point goes through B first. Renormalised so h22 = 1 - every homography in this module is the
   representative with h22 = 1, so composition never silently changes the scale of the entries. */
export const hMul = (A, B) => {
  if (!A || !B) return null;
  const a = [A[0], A[1], A[2], A[3], A[4], A[5], A[6], A[7], 1];
  const b = [B[0], B[1], B[2], B[3], B[4], B[5], B[6], B[7], 1];
  const m = new Array(9);
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
    m[r * 3 + c] = a[r * 3] * b[c] + a[r * 3 + 1] * b[3 + c] + a[r * 3 + 2] * b[6 + c];
  }
  if (Math.abs(m[8]) < 1e-12) return null;
  const k = 1 / m[8];
  return [m[0] * k, m[1] * k, m[2] * k, m[3] * k, m[4] * k, m[5] * k, m[6] * k, m[7] * k];
};

export const hTranslate = (dx, dy) => [1, 0, dx || 0, 0, 1, dy || 0, 0, 0];

/* a CSS 2-D matrix(a b c d e f) as a homography: x' = a x + c y + e, y' = b x + d y + f */
export const hAffine = (a, b, c, d, e, f) => [a, c, e || 0, b, d, f || 0, 0, 0];

/* the same map applied ABOUT a point - what an impact squash on a card wants (its own bottom centre) */
export const hAbout = (h, ox, oy) => hMul(hTranslate(ox, oy), hMul(h, hTranslate(-ox, -oy)));

const fx = (v) => (Object.is(v, -0) ? 0 : v).toFixed(9);

/* THE CSS. matrix3d takes the 4x4 COLUMN MAJOR; a planar homography lifts into it by leaving z alone and putting the
   perspective terms where the browser's per-pixel divide reads them:
     m11 = h00, m21 = h01, m41 = h02      so X' = h00 x + h01 y + h02
     m12 = h10, m22 = h11, m42 = h12      so Y' = h10 x + h11 y + h12
     m14 = h20, m24 = h21, m44 = 1        so W' = h20 x + h21 y + 1
   Fixed decimals (9 places): the perspective terms are ~1e-4 per px and must not be rounded to nothing, and a fixed
   format keeps a frame a pure function of t on any machine. */
export const cssMatrix3d = (h) => {
  if (!h) return "none";
  const m = [h[0], h[3], 0, h[6], h[1], h[4], 0, h[7], 0, 0, 1, 0, h[2], h[5], 0, 1];
  return "matrix3d(" + m.map(fx).join(", ") + ")";
};

/* the quad's bounding rectangle in the same units the quad is given in */
export const quadBounds = (quad) => {
  const p = quadPoints(quad);
  if (!p) return null;
  const xs = p.map((q) => q[0]), ys = p.map((q) => q[1]);
  const x = Math.min(...xs), y = Math.min(...ys);
  return { x, y, w: Math.max(...xs) - x, h: Math.max(...ys) - y };
};

/* THE CARD'S UNPROJECTED BOX: the card's own aspect (height over width), letterboxed inside the quad's bounding
   rectangle and centred there. The card is laid out at THIS size - real pixels, real type - and only then projected,
   so its type is set at a readable size and the perspective is applied to finished pixels rather than to a layout. */
export const embedBox = (quad, aspect) => {
  const b = quadBounds(quad);
  if (!b || !(b.w > 0) || !(b.h > 0)) return null;
  const a = num(+aspect) && +aspect > 0 ? +aspect : b.h / b.w;
  const w = a * b.w <= b.h ? b.w : b.h / a, h = a * w;
  return { x: b.x + (b.w - w) / 2, y: b.y + (b.h - h) / 2, w, h };
};

/* THE ELEMENT'S TRANSFORM: from the card's OWN coordinates (0..box.w, 0..box.h, its origin at its top left) to the
   offset from that same origin that lands it on the surface. That is what a CSS transform with `transform-origin:
   0 0` composes to on an element already positioned at box.x / box.y, so the element's layout box is left alone and
   the projection is one matrix. The box's place inside the quad's bounding rectangle is carried through, which is
   what letterboxes the card on the surface instead of stretching it to the corners. */
export const embedMatrix = (quad, box) => {
  const b = quadBounds(quad), H = hFromUnitSquare(quad);
  if (!b || !H || !box || !(box.w > 0) || !(box.h > 0) || !(b.w > 0) || !(b.h > 0)) return null;
  const toUnit = [1 / b.w, 0, (box.x - b.x) / b.w, 0, 1 / b.h, (box.y - b.y) / b.h, 0, 0];
  return hMul(hTranslate(-box.x, -box.y), hMul(H, toUnit));
};

/* a rectangle INSIDE the card (the quoted phrase, a badge) carried onto the surface: its four projected corners in
   order and their bounding box - the quad for anything drawn in the projected space (the underline rides the bottom
   edge), the box for anything that still wants an axis-aligned target. `r` and `box` are in stage coordinates, `m`
   the matrix above (written as an offset from the box's own origin). */
export const embedRegion = (m, box, r) => {
  if (!m || !box || !r) return null;
  const corners = [[r.x, r.y], [r.x + r.w, r.y], [r.x + r.w, r.y + r.h], [r.x, r.y + r.h]];
  const out = [];
  for (const [cx, cy] of corners) {
    const p = hApply(m, cx - box.x, cy - box.y);
    if (!p) return null;
    out.push([p[0] + box.x, p[1] + box.y]);
  }
  const xs = out.map((p) => p[0]), ys = out.map((p) => p[1]);
  const x = Math.min(...xs), y = Math.min(...ys);
  return { quad: out, x, y, w: Math.max(...xs) - x, h: Math.max(...ys) - y };
};
