/* kinetics/camera.mjs - THE CAMERA (P49 T1-T3): one persistent 2D similarity per timeline - a zoom s, the world point it
   LOOKS at, and the screen point that look-point lands AT - as a pure function of t. SOURCE OF TRUTH, inlined into the
   scene-evidence player by sync_kinetics.py between KINETICS:BEGIN camera and KINETICS:END, after chartxf. Self-contained:
   nothing here reads a template symbol (its clamp is its own).
     screen = at + s * (p - look)          (43 s43.2: p_screen = M_camera x M_world x p_local)
   at == look is a zoom IN PLACE about the target (the punch, the focus zoom, the pull-back - the three species the player
   shipped with, whose envelopes are factored here UNCHANGED so the frames are pixel-identical); at != look is a PAN.
   Bravos, measured 2026-09-10 (P49's amendment): 37 of 45 held compositions are camera-still - LOCKED is the default;
   the camera moves for a stage wider than the frame or tied to a landing (E51), never as a drift on a held chart. */

export const CAM = Object.freeze({
  PUNCH_IN: 0.42, PUNCH_OUT: 0.5, PUNCH_SCALE: 1.14,   /* the punch: in - hold - out, cubic ease (yt-camera-move) */
  FOCUS_SCALE: 1.32,                                     /* the focus zoom: zoom + pan to the anchor, then dead still (the servo law) */
  PULL_FROM: 1.9,                                        /* the pull-back: opens ON the number, one decelerating pull */
});
const camClamp = (k) => Math.min(1, Math.max(0, k));
export const camEase = Object.freeze({
  cubic: (k) => 1 - Math.pow(1 - camClamp(k), 3),                                                 /* the species' spEase */
  inout: (k) => { k = camClamp(k); return k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; },   /* the species' spIO */
  linear: (k) => camClamp(k),
  hold: (k) => (camClamp(k) >= 1 ? 1 : 0),                                                        /* the previous key holds, then steps */
});
export const CAM_EASES = Object.freeze(Object.keys(camEase));

/* the identity: the stage, unmoved */
export const camIdentity = (W, H) => ({ s: 1, look: [W / 2, H / 2], at: [W / 2, H / 2] });

/* a camera SPECIES window (punch | focus_zoom | pull_back) at fraction k of its clock, about the target's centre c -
   the exact envelopes camXf drew (P35 T6), so a flag flip changes no pixel; null outside the window */
export const camSpeciesState = (kind, k, c, dur, P = CAM) => {
  if (k < 0 || k > 1) return null;
  let s = 1;
  if (kind === "punch") {
    const tin = P.PUNCH_IN / (dur || 1), tout = P.PUNCH_OUT / (dur || 1);
    const a = k < tin ? camEase.cubic(k / tin) : k > 1 - tout ? 1 - camEase.cubic((k - (1 - tout)) / tout) : 1;
    s = 1 + (P.PUNCH_SCALE - 1) * a;
  } else if (kind === "focus_zoom") s = 1 + (P.FOCUS_SCALE - 1) * camEase.inout(Math.min(1, k * 1.8));
  else if (kind === "pull_back") s = P.PULL_FROM + (1 - P.PULL_FROM) * camEase.cubic(k);
  else return null;
  return { s, look: [c[0], c[1]], at: [c[0], c[1]] };
};

/* AUTHORED KEYS: [{t, zoom, look:[x,y], at:[x,y]|undefined, ease}] in stage px, sorted by t. Before the first key the
   camera is identity; between keys s, look and at lerp by the segment's ease (named on the key the segment ARRIVES at);
   after the last key it holds. A key with no `at` looks in place (at = look). */
export const camKeyState = (keys, t, W, H) => {
  if (!keys || !keys.length) return camIdentity(W, H);
  const norm = (k) => ({ t: +k.t, s: +k.zoom > 0 ? +k.zoom : 1, look: k.look ? [+k.look[0], +k.look[1]] : [W / 2, H / 2],
                         at: k.at ? [+k.at[0], +k.at[1]] : (k.look ? [+k.look[0], +k.look[1]] : [W / 2, H / 2]), ease: camEase[k.ease] || camEase.cubic });
  const K = keys.map(norm);
  if (t <= K[0].t) return t < K[0].t ? camIdentity(W, H) : { s: K[0].s, look: K[0].look, at: K[0].at };
  let i = 1; while (i < K.length && t > K[i].t) i++;
  if (i >= K.length) { const L = K[K.length - 1]; return { s: L.s, look: L.look, at: L.at }; }
  const a = K[i - 1], b = K[i], u = b.ease(camClamp((t - a.t) / Math.max(1e-6, b.t - a.t)));
  const L = (p, q) => p + (q - p) * u;
  return { s: L(a.s, b.s), look: [L(a.look[0], b.look[0]), L(a.look[1], b.look[1])], at: [L(a.at[0], b.at[0]), L(a.at[1], b.at[1])] };
};

/* the CSS for a state, about a transform-origin at the stage's centre. at == look keeps the string the player has always
   written (byte-identical -> pixel-identical); a pan takes the general form: translate(t) scale(s) with
   t = at - s*look - (1 - s)*O, which is the same mapping screen = at + s (p - look) under that origin. */
export const camCssFor = (st, W, H) => {
  const [lx, ly] = st.look, [ax, ay] = st.at, s = st.s;
  if (ax === lx && ay === ly) {
    return s === 1 ? "" : "translate(" + (lx - W / 2).toFixed(1) + "px, " + (ly - H / 2).toFixed(1) + "px) scale(" + s.toFixed(4)
      + ") translate(" + (W / 2 - lx).toFixed(1) + "px, " + (H / 2 - ly).toFixed(1) + "px)";
  }
  const tx = ax - s * lx - (1 - s) * W / 2, ty = ay - s * ly - (1 - s) * H / 2;
  return "translate(" + tx.toFixed(2) + "px, " + ty.toFixed(2) + "px) scale(" + s.toFixed(4) + ")";
};

/* the FRUSTUM: the stage rectangle in world (pre-camera) coordinates - p = look + (screen - at) / s */
export const camFrustum = (st, W, H) => {
  const [lx, ly] = st.look, [ax, ay] = st.at, s = st.s;
  return { x0: lx + (0 - ax) / s, y0: ly + (0 - ay) / s, x1: lx + (W - ax) / s, y1: ly + (H - ay) / s };
};
/* a world box {x, y, w, h} against the frustum: fully inside, the visible share of its area, and its on-screen scale */
export const camInFrame = (fr, box, s = 1) => {
  const x0 = Math.max(fr.x0, box.x), y0 = Math.max(fr.y0, box.y), x1 = Math.min(fr.x1, box.x + box.w), y1 = Math.min(fr.y1, box.y + box.h);
  const area = Math.max(0, box.w) * Math.max(0, box.h);
  const vis = area > 0 ? Math.max(0, x1 - x0) * Math.max(0, y1 - y0) / area : (x0 <= x1 && y0 <= y1 ? 1 : 0);   /* a point: in or out */
  return { inside: box.x >= fr.x0 && box.y >= fr.y0 && box.x + box.w <= fr.x1 && box.y + box.h <= fr.y1, visible: vis, scale: s };
};
/* T4 - THE ATTENTION LAW (P49), locked by default (Bravos). With `attention: "landings"` a dock that ARRIVES (throw | land)
   pulls the eye: a zoom in place of ATTN.SCALE about the card's parked box, in over ATTN.IN from the CONTACT frame (E51: a
   push is tied to a landing - never to a thing that just sits there), held while the card is up, released over ATTN.OUT
   before it leaves. contactOf(dock) is the player's (the stop-action clock: a throw's FLIGHT_S, a landing's ANTIC_S + DROP_S).
   [DERIVED: Bravos #68's map push ~6 % between countries, then still; D1's 15 deg cone] - HG1 tunes the three by eye. */
export const ATTN = Object.freeze({ SCALE: 1.06, IN: 0.5, OUT: 0.6 });
export const camAttentionState = (docks, t, contactOf, P = ATTN) => {
  let st = null;
  for (const d of docks || []) {
    if (!d || !d.place || !(d.arrive === "throw" || d.arrive === "land")) continue;
    const tc = contactOf(d), exit = +d.exit, out = exit - P.OUT;
    if (!(t >= tc && t <= exit)) continue;
    const a = camEase.inout(camClamp((t - tc) / P.IN)) * (1 - camEase.inout(camClamp((t - out) / P.OUT)));
    const c = [d.place.x + d.place.w / 2, d.place.y + d.place.h / 2];
    st = { s: 1 + (P.SCALE - 1) * a, look: c, at: c };   /* the last landing wins, as the last species window does */
  }
  return st;
};
/* where a world point lands on screen */
export const camProject = (st, p) => [st.at[0] + st.s * (p[0] - st.look[0]), st.at[1] + st.s * (p[1] - st.look[1])];
