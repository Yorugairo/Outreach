/* species/flow.mjs - THE FLOW DIAGRAM (P50 T4; the Bravos flow diagram, shots 82-86: a three-node diagram
   draws on a word, and on a LATER word one node swaps while the rest stands - the rhyme). SOURCE OF TRUTH,
   inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN flow and KINETICS:END,
   AFTER spring, idle, clothoid and chip - it imports all four, and the import order IS the region order.

   WHEN: the sentence EXPLAINS a mechanism - A causes B via C - as named things and the arrows between them;
   a later word SWAPS one node and the rest stands (Bravos's rhyme).

   THE LAW, all of it a pure function of t:
     box    - the dashed frame draws ON, dash by dash, by the curvature stroke (42 s42.1): the nib runs round
              the rectangle and leaves DASH-long marks with GAP between them, so the diagram arrives as a
              drawn thing and not as a rectangle that appeared. A dash already passed is simply there.
     nodes  - each node is a CHIP (species/chip.mjs): the same card, the same sourced glyph, the same badge
              spring, landing NODE_STEP after the one before, once the box is BOX_LEAD of the way round.
              The chip's own painter is not called - a chip resolves its own target and owns its own cross -
              but its dials (CHIP) and its landing law (chipLand) are, so a node and a lone chip land alike.
     arrows - between named nodes, one per EDGE_S after the last node lands, drawn BY LENGTH with the nib:
              a CLOTHOID (kinetics/clothoid.mjs, 42 s42.4), leaving one chip's edge on a tangent turned BOW
              off the chord and entering the next's turned BOW * ENTER_K back into it. The two turns are
              UNEQUAL on purpose: equal ones give a circular arc, and the point of the fitter is the RAMP -
              dk/ds constant, the pen accelerating out of one card and settling into the next.
     swap   - on swap.at the standing node UN-DRAWS - its own landing run backward, exactly as chart_to's
              recast runs a build law backward - and the new glyph and label draw on IN THE SAME SPOT. The
              arrows stand: the mechanism did not change, one of its parts did. ONE event at swap.at.
     tag    - a year stamp in the box's corner, written last (the diagram is dated, not captioned).
   Nothing is stored: every visual reads from t, sp.at and sp.swap.at, so a scrubbed frame is the played
   frame. The glyphs are SOURCED icons (assets/icons, A2a provenance) carried in the asset map as
   `icon:<name>`; this module never invents geometry. The dials below are ours to tune (42 s42.5). */
import { springPop } from "../kinetics/spring.mjs";
import { idleXf } from "../kinetics/idle.mjs";
import { clothoid, clothoidPath } from "../kinetics/clothoid.mjs";
import { CHIP, chipLand, chipGeometry } from "./chip.mjs";

export const FLOW = Object.freeze({
  BOX_S: 0.9,        /* the dashed frame's own draw: long enough that the nib is seen going round, short enough that the first chip is not kept waiting */
  BOX_LEAD: 0.55,    /* ... and the share of it that is done when the first chip lands - the frame is still drawing under the diagram, the way a hand works */
  DASH: 26,          /* the dash's length in STAGE px ... */
  DASH_GAP: 15,      /* ... and the air between two dashes: a 2:1 rhythm reads as "a frame", never as a solid box */
  NODE_STEP: 0.2,    /* one node after the last: a beat under the eye's own saccade, so three read as a sequence and not a flash */
  EDGE_LAG: 0.1,     /* the breath between the last chip landing and the first arrow leaving it */
  EDGE_S: 0.34,      /* one arrow, drawn by length; arrows go one at a time - the mechanism is read in its order */
  BOW: 0.42,         /* the exit tangent's turn off the chord, in radians: enough curve to read as a hand's arrow, not a hoop */
  ENTER_K: 0.45,     /* ... and the entry tangent's turn as a share of it. UNEQUAL: equal angles are a circular arc and waste the fitter */
  EDGE_GAP: 16,      /* the air between a card's edge and the arrow that leaves it */
  HEAD: 28,          /* the arrowhead's stroke length in stage px ... */
  HEAD_A: 0.42,      /* ... and its half-angle in radians */
  HEAD_F: 0.72,      /* ... landing over the last of the arrow's own clock, after the shaft has arrived */
  SAMPLES: 40,       /* the clothoid's polyline per arrow: dense enough that its chords hide at our sizes */
  SWAP_OUT_S: 0.3,   /* the standing node's landing, run BACKWARD */
  SWAP_IN_S: 0.45,   /* ... and the new one's, run forward: in is slower than out, so the eye lands on what arrived */
  TAG_LAG: 0.12,     /* the breath before the year stamps ... */
  TAG_S: 0.5,        /* ... and its own write */
  TAG_PAD: 26,       /* the stamp's inset from the box's top-right corner */
  TAG_SIZE: 34,      /* ... at this size: a date, not a title */
  PITCH_K: 1.5,      /* a node's room ALONG the row as a multiple of the card: the card plus the arrow between it and the next */
  CROSS_K: 1.15,     /* ... and ACROSS it, over card + label: a breath above and below */
  MIN_K: 0.4,        /* the smallest the diagram may be scaled to before it stops being read - under it the author gave it too small a box */
  LABEL_H: 34,       /* the label's own line, for the block's height (the chip writes it at CHIP.LABEL_DY below the card) */
});

const flow01 = (v) => Math.min(1, Math.max(0, v));

/* THE LAYOUT: where each node stands inside the declared box, and how big the whole diagram is drawn.
   A row inside the box; a COLUMN when the box is taller than it is wide (a portrait build's box is), which
   is the same rule read from the geometry rather than from the aspect. */
export const flowLayout = (box, n) => {
  const N = Math.max(1, n | 0), column = box.h > box.w;
  const pitch = (column ? box.h : box.w) / N, across = column ? box.w : box.h;
  const block = CHIP.SIZE + CHIP.LABEL_DY + FLOW.LABEL_H;
  const k = Math.max(FLOW.MIN_K, Math.min(1, pitch / (CHIP.SIZE * FLOW.PITCH_K), across / (block * FLOW.CROSS_K)));
  const lift = (CHIP.LABEL_DY + FLOW.LABEL_H) * k / 2;   /* the card sits above centre so card + label are centred together */
  const cells = [];
  for (let i = 0; i < N; i++) {
    cells.push(column ? { x: box.x + box.w / 2, y: box.y + pitch * (i + 0.5) - lift }
                      : { x: box.x + pitch * (i + 0.5), y: box.y + box.h / 2 - lift });
  }
  return { k, column, cells, half: CHIP.SIZE * k / 2 };
};

/* THE CLOCK: every instant the declaration implies, in episode seconds. One place, so the painter, the tests
   and the gate all read the same schedule. */
export const flowClock = (sp) => {
  const at = +sp.at, nodes = sp.nodes || [], edges = sp.edges || [];
  const first = at + FLOW.BOX_S * FLOW.BOX_LEAD;
  const nodeAt = nodes.map((_, i) => first + i * FLOW.NODE_STEP);
  const landed = (nodeAt.length ? nodeAt[nodeAt.length - 1] : first) + CHIP.LAND_S;
  const edgeAt = edges.map((_, j) => landed + FLOW.EDGE_LAG + j * FLOW.EDGE_S);
  const tagAt = (edgeAt.length ? edgeAt[edgeAt.length - 1] + FLOW.EDGE_S : landed) + FLOW.TAG_LAG;
  return { box: [at, at + FLOW.BOX_S], nodeAt, landed, edgeAt, tagAt, tagEnd: tagAt + FLOW.TAG_S };
};

/* the box's draw at t, 0..1 - and, from it, the dash that is under the nib */
export const flowBoxF = (sp, t) => flow01((t - +sp.at) / FLOW.BOX_S);

/* the rectangle's perimeter cut into dashes, each with the fraction of the whole draw it owns. The nib starts
   at the top-left and runs clockwise - the way the box would be drawn by a hand. */
export const flowDashes = (box) => {
  const per = 2 * (box.w + box.h), n = Math.max(4, Math.round(per / (FLOW.DASH + FLOW.DASH_GAP)));
  const step = per / n, out = [];
  const at = (d) => {   /* a distance round the perimeter -> a point on it, clockwise from the top-left */
    let s = ((d % per) + per) % per;
    if (s < box.w) return { x: box.x + s, y: box.y };
    s -= box.w;
    if (s < box.h) return { x: box.x + box.w, y: box.y + s };
    s -= box.h;
    if (s < box.w) return { x: box.x + box.w - s, y: box.y + box.h };
    return { x: box.x, y: box.y + box.h - (s - box.w) };
  };
  const corners = [box.w, box.w + box.h, 2 * box.w + box.h, per];
  for (let i = 0; i < n; i++) {
    const d0 = i * step;
    let len = Math.min(FLOW.DASH, step * 0.72);
    /* a dash that ran past a CORNER used to be drawn as its chord, which cut the corner off the box (read in
       the frame, 2026-09-11). A dash stops at the corner it reaches; the next one starts the new side. */
    for (const c of corners) if (c > d0 && c < d0 + len) len = c - d0;
    out.push({ a: at(d0), b: at(d0 + len), t0: i / n, t1: (i + 1) / n });
  }
  return out;
};

/* THE SWAP at t: which node is changing, and how far through which half of its change. `phase` is "none"
   before the word, "out" while the standing node un-draws, "in" while the new one draws, "done" after. */
export const flowSwapPhase = (sp, t) => {
  const sw = sp.swap;
  if (!sw || !Number.isFinite(+sw.at)) return { phase: "none", u: 1 };
  const d = t - +sw.at;
  if (d < 0) return { phase: "none", u: 1 };
  if (d < FLOW.SWAP_OUT_S) return { phase: "out", u: 1 - d / FLOW.SWAP_OUT_S };   /* the landing, run backward */
  const uIn = flow01((d - FLOW.SWAP_OUT_S) / FLOW.SWAP_IN_S);
  return { phase: uIn >= 1 ? "done" : "in", u: uIn };
};

/* ONE NODE at t: what it shows (a swap changes the glyph and the label, never the place) and how far its
   landing has run. u is the landing's normalised clock, which is all chipLand needs. */
export const flowNodeAt = (sp, i, t) => {
  const node = (sp.nodes || [])[i] || {}, sw = sp.swap;
  const C = flowClock(sp), u0 = flow01((t - C.nodeAt[i]) / CHIP.LAND_S);
  if (!sw || sw.node !== node.id) return { icon: node.icon, label: node.label, u: u0, alpha: 1, swapping: false };
  const ph = flowSwapPhase(sp, t);
  if (ph.phase === "none") return { icon: node.icon, label: node.label, u: u0, alpha: 1, swapping: false };
  /* OUT: the landing run backward - and the card's own opacity on the OUT clock. The chip's fade is 0.14 s
     of a 0.55 s landing; reversed into SWAP_OUT_S it would be a blink at the very end rather than an
     un-draw (read in the frame, 2026-09-11), so the ink leaves on the clock the un-draw was given, the way
     an `undraw` retracts a stroke on its own clock and not on the build's. */
  if (ph.phase === "out") return { icon: node.icon, label: node.label, u: Math.min(u0, ph.u), alpha: ph.u, swapping: true };
  return { icon: sw.icon, label: sw.label, u: ph.u, alpha: 1, swapping: ph.phase === "in" };
};

/* the pose of a node at a landing clock u: the chip's own law, on the flow's clock */
export const flowPose = (u) => chipLand(flow01(u) * CHIP.LAND_S, 0);

/* ONE ARROW's draw at t, 0..1 */
export const flowEdgeF = (sp, j, t) => {
  const C = flowClock(sp);
  return C.edgeAt[j] === undefined ? 0 : flow01((t - C.edgeAt[j]) / FLOW.EDGE_S);
};

/* THE ANCHORS of one arrow: the point on each card's square edge that faces the other, pushed out by
   EDGE_GAP, and the two tangents the clothoid is fitted to. */
export const flowAnchors = (a, b, half) => {
  const dx = b.x - a.x, dy = b.y - a.y, chord = Math.atan2(dy, dx);
  const edge = (c, th) => {   /* the square's boundary in direction th, plus the air */
    const cs = Math.cos(th), sn = Math.sin(th), m = Math.max(Math.abs(cs), Math.abs(sn)) || 1;
    const r = half / m + FLOW.EDGE_GAP;
    return { x: c.x + r * cs, y: c.y + r * sn };
  };
  const t0 = chord - FLOW.BOW, t1 = chord + FLOW.BOW * FLOW.ENTER_K;
  return { p0: edge(a, t0), t0, p1: edge(b, t1 + Math.PI), t1, chord };
};

/* the arrowhead's two strokes at the polyline's far end, along the tangent it arrives on */
export const flowHead = (pts) => {
  const n = pts.length;
  if (n < 2) return "";
  const tip = pts[n - 1], prev = pts[n - 2], th = Math.atan2(tip.y - prev.y, tip.x - prev.x);
  const arm = (s) => ({ x: tip.x - FLOW.HEAD * Math.cos(th + s * FLOW.HEAD_A), y: tip.y - FLOW.HEAD * Math.sin(th + s * FLOW.HEAD_A) });
  const l = arm(1), r = arm(-1);
  return "M" + l.x.toFixed(2) + " " + l.y.toFixed(2) + " L" + tip.x.toFixed(2) + " " + tip.y.toFixed(2)
       + " L" + r.x.toFixed(2) + " " + r.y.toFixed(2);
};

/* the edges as index pairs into the node list (a name that is not a node is dropped, not drawn wrong) */
export const flowEdgeIndex = (sp) => {
  const ids = (sp.nodes || []).map((n) => n && n.id);
  return (sp.edges || []).map((e) => [ids.indexOf(e && e[0]), ids.indexOf(e && e[1])]);
};

/* THE PAINTER. ctx is the template's species context (see SPECIES_PAINTERS in the player). Everything is
   drawn in STAGE px into one group, in reading order: the frame, the arrows (under the cards, so their ends
   tuck beneath), the cards, the stamp. */
export function paintFlow(ctx) {
  const { sp, t, svg, el, A, resolveTarget, drawOn, hash, idle, seed, si } = ctx;
  const box = resolveTarget(sp.target);
  if (!box || !(box.w > 0 && box.h > 0)) return;   /* the targeting law: a flow needs its room declared */
  const nodes = sp.nodes || [], lay = flowLayout(box, nodes.length), C = flowClock(sp);
  const g = el("g", "flow", svg, {});
  /* the frame, dash by dash, under the nib */
  const bf = flowBoxF(sp, t);
  if (bf > 0) {
    for (const d of flowDashes(box)) {
      const f = flow01((bf - d.t0) / Math.max(1e-6, d.t1 - d.t0));
      if (f <= 0) continue;
      const p = el("path", "flowbox", g, { d: "M" + d.a.x.toFixed(1) + " " + d.a.y.toFixed(1) + " L" + d.b.x.toFixed(1) + " " + d.b.y.toFixed(1) });
      if (f < 1) drawOn(p, f);
    }
  }
  /* the arrows, drawn by length with the nib */
  flowEdgeIndex(sp).forEach(([ia, ib], j) => {
    if (ia < 0 || ib < 0 || ia === ib) return;
    const f = flowEdgeF(sp, j, t);
    if (f <= 0) return;
    const an = flowAnchors(lay.cells[ia], lay.cells[ib], lay.half);
    const pts = clothoid(an.p0, an.t0, an.p1, an.t1, FLOW.SAMPLES);
    drawOn(el("path", "flowarrow", g, { d: clothoidPath(pts) }), Math.min(1, f / FLOW.HEAD_F));
    if (f > FLOW.HEAD_F) drawOn(el("path", "flowarrow", g, { d: flowHead(pts) }), (f - FLOW.HEAD_F) / (1 - FLOW.HEAD_F));
  });
  /* the cards */
  nodes.forEach((node, i) => {
    const st = flowNodeAt(sp, i, t);
    if (st.u <= 0 || st.alpha <= 0) return;
    const pose = flowPose(st.u), c = lay.cells[i];
    const ix = sp.idle && sp.idle !== "none" ? idle(sp.idle, t, hash(seed | 0, si | 0, 907 + i)) : { scale: 1, dx: 0, dy: 0 };
    const s = pose.scale * ix.scale * lay.k;
    const ng = el("g", "", g, { opacity: (pose.fade * st.alpha).toFixed(3),
                                transform: "translate(" + (c.x + ix.dx).toFixed(1) + " " + (c.y + (pose.dy + ix.dy) * lay.k).toFixed(1) + ") scale(" + s.toFixed(4) + ")" });
    const h = CHIP.SIZE / 2;
    el("rect", "chipcard", ng, { x: (-h).toFixed(1), y: (-h).toFixed(1), width: CHIP.SIZE, height: CHIP.SIZE, rx: CHIP.RX });
    const geo = chipGeometry(A ? A["icon:" + st.icon] : null);
    if (geo) {
      const vb = geo.vb || [0, 0, 24, 24], gk = CHIP.GLYPH / Math.max(vb[2] || 1, vb[3] || 1);
      const gg = el("g", "chipglyph", ng, { transform: "translate(" + (-CHIP.GLYPH / 2).toFixed(1) + " " + (-CHIP.GLYPH / 2).toFixed(1) + ") scale(" + gk.toFixed(4) + ") translate(" + (-vb[0]) + " " + (-vb[1]) + ")" });
      geo.el.forEach((q) => el(q.t, "", gg, q.a));   /* the sourced geometry verbatim */
    }
    if (st.label) { const lab = el("text", "chiplab", ng, { x: 0, y: (h + CHIP.LABEL_DY).toFixed(1) }); lab.textContent = st.label; }
  });
  /* the year stamp in the box's corner */
  if (sp.tag && t >= C.tagAt) {
    const u = flow01((t - C.tagAt) / FLOW.TAG_S), e = springPop(u);
    const tx = el("text", "flowtag", g, { x: (box.x + box.w - FLOW.TAG_PAD).toFixed(1),
                                          y: (box.y + FLOW.TAG_PAD + FLOW.TAG_SIZE * (1.4 - 0.4 * e)).toFixed(1),
                                          opacity: flow01(u / 0.4).toFixed(3), style: "font-size:" + FLOW.TAG_SIZE + "px" });
    tx.textContent = sp.tag;
  }
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the template's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.flow = paintFlow;
