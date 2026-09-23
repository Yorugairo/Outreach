/* kinetics/camera.mjs - THE CAMERA (P49 T1-T3): one persistent 2D similarity per timeline - a zoom s, the world point it
   LOOKS at, and the screen point that look-point lands AT - as a pure function of t. SOURCE OF TRUTH, inlined into the
   scene-evidence player by sync_kinetics.py between KINETICS:BEGIN camera and KINETICS:END, after chartxf. Self-contained:
   nothing here reads a template symbol (its clamp is its own).
     screen = at + s * (p - look)          (43 s43.2: p_screen = M_camera x M_world x p_local)
   at == look is a zoom IN PLACE about the target (the punch, the focus zoom, the pull-back - the three species the player
   shipped with, whose envelopes are factored here UNCHANGED so the frames are pixel-identical); at != look is a PAN.
   Bravos, measured 2026-09-10 (P49's amendment): 37 of 45 held compositions are camera-still - LOCKED is the default;
   the camera moves for a stage wider than the frame or tied to a landing (E51), never as a drift on a held chart. */

/* P58 T3 - THE DEPTH TERM. One eye still (E59): the camera is ONE state per timeline, and a plate that ships in
   PLANES (doc 24 "2.5D depth planes"; `<plate>.layers.json`, P58 T2) hands each plane a parallax factor k. A layer
   at k takes the SHARE k of this one camera's translation (at - look) and of its zoom (s - 1):
     screen_k = look + (at - look) * k + (1 + (s - 1) * k) * (p - look)
   so k = 1 IS the camera above - the flat plate, arithmetic-identical - k > 1 moves MORE (nearer the eye) and k < 1
   less. Parallax is therefore a CONSEQUENCE of the move the row already authored, never a mechanism of its own: with
   the camera LOCKED (s = 1, at == look - the default, 37 of 45 Bravos compositions) every k collapses to the identity
   and a layered world paints exactly the flat composite of its planes. E49 holds: nothing here adds a move.
   THE TWO CITATIONS, and which one this code is.
     - doc 24 `24-COMPOSITION-AND-SCALE-SPEC.md:156` (`parallax_factor`: -far 1.0 / -board 1.05 / -mid 1.15 /
       -near 1.40) - the doctrine this implements. The role -> k table is the COMPILER'S (build_plate_library.py
       LAYER_PLANES, P58 T2) and k arrives here on the timeline, so there is ONE table and it is not this file's.
     - the monograph `sources/reference_analyses/ACADEMIC_LITERATURE_DRAWING_AND_2_5D_ANIMATION_ENGINE.md:195-205`
       s2.4: `Delta x = f * t_perp * (1/z2 - 1/z1)` - the same statement in INVERSE DEPTH. This module implements
       doc 24's form: a 2D similarity has no focal length f and no per-pixel z, so the pinhole's `f * t_perp / z`
       reduces to one scalar per PLANE - k = z_ref / z_layer, the normalised inverse-depth ratio, which IS doc 24's
       factor. The displacement between two planes is then (at - look) * (k2 - k1): s2.4's Delta x with f * t_perp
       folded into the camera's own translation. P58 T1 proved the same statement in PIL on 18 frames
       (`probe_2_5d.py`: offset = (at - look) * k, scale = 1 + (s - 1) * k); this is that law in the camera's form.
   OPEN DECISION 5 (the parent's answer, 2026-09-14): an ART-embed surface keeps its OWN quad - it is measured off
   the still - and the layer's k applies to the PLATE BEHIND IT, never to the card on the surface. No embed golden
   moves because of this term. */
export const PARALLAX = Object.freeze({
  FLAT: 1,        /* the flat plate, and doc 24's `-far` wall: the share at which this term IS the camera above */
  K_MIN: 0,       /* a plane that takes none of the move (a thing pinned to the frame, not standing in the world) */
  K_MAX: 4,       /* the compiler's own ceiling (build_plate_library: `0 < depth <= 4`), mirrored here as a clamp */
});

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
/* T4 - THE ATTENTION LAW (P49), locked by default (Bravos). With `attention: "landings"` a dock that ARRIVES (throw | land
   | stamp) pulls the eye: a zoom in place of ATTN.SCALE about the card's parked box, in over ATTN.IN from the CONTACT frame
   (E51: a push is tied to a landing - never to a thing that just sits there), held while the card is up, released over
   ATTN.OUT before it leaves. contactOf(dock) is the player's (the stop-action clock: a throw's FLIGHT_S, a landing's
   ANTIC_S + DROP_S, a stamp's STAMP_LAND.tc - P69 T4, R26-247: the clamped scale spring's crossing, the instant the mark
   is its own size; the gate mirrors it as STAMP_CONTACT_S). [DERIVED: Bravos #68's map push ~6 % between countries, then
   still; D1's 15 deg cone] - HG1 tunes the three by eye. */
export const ATTN = Object.freeze({ SCALE: 1.06, IN: 0.5, OUT: 0.6 });
export const camAttentionState = (docks, t, contactOf, P = ATTN) => {
  let st = null;
  for (const d of docks || []) {
    if (!d || !d.place || !(d.arrive === "throw" || d.arrive === "land" || d.arrive === "stamp")) continue;
    const tc = contactOf(d), exit = +d.exit, out = exit - P.OUT;
    if (!(t >= tc && t <= exit)) continue;
    const a = camEase.inout(camClamp((t - tc) / P.IN)) * (1 - camEase.inout(camClamp((t - out) / P.OUT)));
    const c = [d.place.x + d.place.w / 2, d.place.y + d.place.h / 2];
    st = { s: 1 + (P.SCALE - 1) * a, look: c, at: c };   /* the last landing wins, as the last species window does */
  }
  return st;
};
/* T5 - THE CAMERA ARRIVAL (P49): the eye goes to a landed card. Over the arrival's clock u (0..1, eased by the caller)
   the camera looks at the card's centre and carries it to the stage's centre while zooming to the FILL scale - the
   scale at which the card's box (stage px) fills the stage; at u = 1 the frustum IS the card, so the world can switch
   to the page the card is a picture of with no seam. */
export const camArrivalState = (box, u, W, H) => {
  const fill = Math.min(W / Math.max(1, box.w), H / Math.max(1, box.h));
  const c = [box.x + box.w / 2, box.y + box.h / 2], O = [W / 2, H / 2];
  return { s: 1 + (fill - 1) * u, look: c, at: [c[0] + (O[0] - c[0]) * u, c[1] + (O[1] - c[1]) * u], fill };
};
/* where a world point lands on screen */
export const camProject = (st, p) => [st.at[0] + st.s * (p[0] - st.look[0]), st.at[1] + st.s * (p[1] - st.look[1])];

/* P58 T3: THIS camera as the plane at k sees it - the share k of the translation and of the zoom (the law in the
   header). k === FLAT returns the state ITSELF, by identity and not by arithmetic: 1 + (s - 1) * 1 is not exactly s
   in binary floating point (s = 0.1 gives 0.09999999999999998), and the flat plate must be the camera it has always
   been - not a value that rounds to it. k is clamped to the compiler's own range, so a sidecar that got past the
   indexer with nonsense cannot invert a plane. */
export const camLayerState = (st, k) => {
  const kk = Math.min(PARALLAX.K_MAX, Math.max(PARALLAX.K_MIN, +k));
  if (!(kk >= PARALLAX.K_MIN) || kk === PARALLAX.FLAT) return st;   /* the flat plate, and NaN: an unknown depth never moves */
  const [lx, ly] = st.look, [ax, ay] = st.at;
  return { s: 1 + (st.s - 1) * kk, look: [lx, ly], at: [lx + (ax - lx) * kk, ly + (ay - ly) * kk] };
};
/* where a world point on the plane at k lands on screen (camProject at k = 1, exactly) */
export const camProjectAt = (st, p, k) => camProject(camLayerState(st, k), p);
/* the CSS the plane at k gets, about the same stage-centre origin the world layer uses (camCssFor at k = 1, exactly
   - the same string, so a layered world under a LOCKED camera writes what the flat world writes) */
export const camLayerCss = (st, k, W, H) => camCssFor(camLayerState(st, k), W, H);
